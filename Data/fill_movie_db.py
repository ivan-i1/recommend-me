import logging
import time
import pandas as pd
from config.settings import START_DATE_EXTRACTION, END_DATE_EXTRACTION, INTERNAL_IMG_SAVE_PATH
from tmdb.client import TMDBClient
from tmdb import endpoints, helper
from db.connection import get_connection
from db import queries
from vectorized_db import v_helpers

#---------------------------------------
#GenreMov SECTION
#---------------------------------------
def get_genreMov(client, connection, cursor):
    paramGenreMov = endpoints.movie_genres()
    response = client.get(
            endpoint=paramGenreMov["endpoint"], 
            params = paramGenreMov["params"]
        )

    json_GenreMov  = helper.extract_genreMov_list(response)

    for genreMov in json_GenreMov:
        try:
            queries.insert_genreMov(cursor, genreMov)
        except Exception as e:
            logging.error(f"Insert Genre error: {type(e).__name__}: {e}")
        
    connection.commit()
#---------------------------------------

#---------------------------------------
#Movie SECTION
#---------------------------------------

def get_movies(client, connection, cursor, date, page):
    paramMov = endpoints.discover_movies(page,date, date)
    response = client.get(
            endpoint=paramMov["endpoint"], 
            params = paramMov["params"]
        )

    json_movies, movie_genre_json = helper.extract_movies_list(response)

    for movie in json_movies:
        try:
            #Get Actors and Director
            paramMov = endpoints.credits_movies(movie["id_tmdb"])
            response_credits = client.get(
                    endpoint=paramMov["endpoint"], 
                    params = paramMov["params"]
                )
            
            json_cast = response_credits["cast"]
            if json_cast:
                df_cast = pd.DataFrame(json_cast)
                top_5_actors = df_cast.nsmallest(5, 'order')['name'].tolist()
                movie["actors"] = str(top_5_actors)
            else:
                movie["actors"] = ""

            json_crew = response_credits["crew"]
            if json_crew:
                df_crew = pd.DataFrame(json_crew)
                director = df_crew[df_crew['job'] == 'Director']
                movie["director"] = str(director["name"].values[0])
            else:
                movie["director"] = ""

            #Get keywords
            movie["keywords"] = helper.extract_keywords(str(movie["overview"]))

            #Get Images
            download_path = ""
            if movie["poster_path"] is not None:
                download_path = movie["poster_path"]
            else:
                download_path = movie["backdrop_path"]

            img_name = ""
            title = helper.clean_text(movie["title"])
            id_img = helper.clean_text(movie["id_tmdb"])
            img_name = id_img + "_" + title + ".jpg"
            img_path = f"{INTERNAL_IMG_SAVE_PATH}{img_name}"

            if download_path is not None:
                movie["img_path"] = img_path
                client.get_img(download_path, img_name)

            #Insert in DB
            queries.insert_movie(cursor, movie)
        except Exception as e:
            logging.error(f"Insert Movie error: {type(e).__name__}: {e}")

    connection.commit()
#---------------------------------------

#---------------------------------------
#Movie_Genre SECTION
#---------------------------------------
    for movie_id in movie_genre_json:
        try:
            id_mov = queries.get_movie_id(cursor, movie_id)
            for genre in movie_genre_json[movie_id]:
                id_gen = queries.get_genreMov_id(cursor, genre)
                queries.insert_movie_genres(cursor, id_mov, id_gen)
        except Exception as e:
            logging.error(f"Insert Movie_Genre error: {type(e).__name__}: {e}")

    connection.commit()
#---------------------------------------
#Return Number of Pages of Date
    return response["total_pages"]

#---------------------------------------

def vectorized_movies(connection, cursor, year):
    try:
        results_movies, column_names = queries.get_year_movies(cursor, year)
        movie_df = pd.DataFrame(results_movies, columns=column_names)
        
        df_vectorized = v_helpers.movie_vectorized_table(cursor, movie_df)
        
        for index, movie in df_vectorized.iterrows():
            try:
                queries.insert_vectorized_movie(cursor, movie)
            except Exception as e:
                logging.error(f"Loop Insert Vectorized Movie error: {type(e).__name__}: {e}")
                time.sleep(5)
                continue
        
        connection.commit()
        
    except Exception as e:
        logging.error(f"Get Year Movie error: {type(e).__name__}: {e}")
        time.sleep(5)

if __name__ == "__main__":

    logging.basicConfig(
        filename="/app/logs/app.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
        )

    client = TMDBClient()
    connection = get_connection()
    cursor = connection.cursor(buffered=True)
    
    #Get Genders of Movies
    get_genreMov(client, connection, cursor)
    
    #Get Movies
    dateList = helper.generate_dateList(START_DATE_EXTRACTION, END_DATE_EXTRACTION)
    for year in dateList:

        for date in dateList[year]:
            try:
                page = 1
                pageNum = get_movies(client, connection, cursor, str(date), int(page))
                page += 1
                while page <= pageNum:
                    get_movies(client, connection, cursor, str(date), int(page))
                    page += 1
            except Exception as e:
                logging.error(f"Loop Insert Movie error: {type(e).__name__}: {e}")
                time.sleep(60)
                continue
        
        #Vectorice Movies
        vectorized_movies(connection, cursor, year)
        

    cursor.close()
    connection.close()


