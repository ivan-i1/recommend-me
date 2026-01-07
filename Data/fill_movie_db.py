import logging
from config.settings import START_DATE_EXTRACTION, END_DATE_EXTRACTION, INTERNAL_IMG_SAVE_PATH
from tmdb.client import TMDBClient
from tmdb import endpoints, helper
from db.connection import get_connection
from db import queries

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
                connection.commit()
                queries.insert_movie_genres(cursor, id_mov, id_gen)
        except Exception as e:
            logging.error(f"Insert Movie_Genre error: {type(e).__name__}: {e}")

    connection.commit()
#---------------------------------------
#Return Number of Pages of Date
    return response["total_pages"]

if __name__ == "__main__":

    logging.basicConfig(
        filename="/app/logs/app.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
        )

    client = TMDBClient()
    connection = get_connection()
    cursor = connection.cursor()
    
    #Get Genders of Movies
    get_genreMov(client, connection, cursor)
    
    #Get Movies
    dateList = helper.generate_dateList(START_DATE_EXTRACTION, END_DATE_EXTRACTION)
    for date in dateList:
        page = 1
        pageNum = get_movies(client, connection, cursor, str(date), int(page))
        while page < pageNum:
            page += 1
            get_movies(client, connection, cursor, str(date), int(page))

    cursor.close()
    connection.close()


