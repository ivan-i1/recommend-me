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
#Regiones Movie SECTION
#---------------------------------------
def get_regions(client, connection, cursor):
    param = endpoints.watch_provider_regions()
    response = client.get(endpoint=param["endpoint"], params=param["params"])

    countries = helper.extract_countries_list(response)

    for country in countries:
        try:
            queries.insert_country(cursor, country)
        except Exception as e:
            logging.error(f"Insert Country error: {type(e).__name__}: {e}")

    connection.commit()
#---------------------------------------

#---------------------------------------
#Provitors SECTION
#---------------------------------------
def get_providers(client, connection, cursor):
    param = endpoints.watch_providers_movies()
    response = client.get(endpoint=param["endpoint"], params=param["params"])

    providers, provider_countries = helper.extract_providers_list(response)

    # Insert Providers
    for provider in providers:
        try:
            #Download Logo
            logo_path = helper.get_logo_provider(client, provider["logo_path"], provider["tmdb_provider_id"], provider["name"])
            provider["logo_path"] = logo_path
            #Insert Provider
            queries.insert_provider(cursor, provider)
        except Exception as e:
            logging.error(f"Insert Provider error: {type(e).__name__}: {e}")

    connection.commit()

    # Insert Countries (placeholder) + Provider_Countries
    for tmdb_provider_id, countries in provider_countries.items():
        try:
            provider_db_id = queries.get_provider_id(cursor, tmdb_provider_id)
            for entry in countries:
                try:
                    queries.insert_country_if_not_exists(cursor, entry["country_code"])
                    queries.insert_provider_country(
                        cursor,
                        provider_db_id,
                        entry["country_code"],
                        "movie",
                        entry["display_priority"]
                    )
                except Exception as e:
                    logging.error(f"Insert ProviderCountry error ({tmdb_provider_id} - {entry['country_code']}): {type(e).__name__}: {e}")
        except Exception as e:
            logging.error(f"Loop ProviderCountry error: {type(e).__name__}: {e}")

    connection.commit()
#---------------------------------------

#---------------------------------------
#Provitors Movie SECTION
#---------------------------------------
def get_movie_providers(client, connection, cursor, tmdb_movie_id):
    movie_db_id = queries.get_movie_id(cursor, tmdb_movie_id)
    if movie_db_id is None:
        logging.warning(f"Movie {tmdb_movie_id} not found in DB, skipping.")
        return

    param = endpoints.movie_watch_providers(tmdb_movie_id)
    response = client.get(endpoint=param["endpoint"], params=param["params"])

    entries = helper.extract_movie_providers_list(response)

    for entry in entries:
        try:
            provider_db_id = queries.get_provider_id(cursor, entry["tmdb_provider_id"])
            if provider_db_id is None:
                logging.warning(f"Provider {entry['tmdb_provider_id']} not in DB, skipping.")
                continue
            queries.insert_movie_provider(cursor, movie_db_id, provider_db_id, entry["country_code"], entry["provider_type"], entry.get("link"))
        except Exception as e:
            logging.error(f"Insert MovieProvider error ({tmdb_movie_id} - {entry}): {type(e).__name__}: {e}")

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
        # Credits (actors / director)
        try:
            paramMov = endpoints.credits_movies(movie["id_tmdb"])
            response_credits = client.get(endpoint=paramMov["endpoint"], params=paramMov["params"])
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
                movie["director"] = str(director["name"].values[0]) if not director.empty else ""
            else:
                movie["director"] = ""
        except Exception as e:
            logging.error(f"Credits error ({movie['id_tmdb']}): {type(e).__name__}: {e}")
            movie["actors"] = ""
            movie["director"] = ""

        # Keywords
        try:
            movie["keywords"] = helper.extract_keywords(str(movie["overview"]))
        except Exception as e:
            logging.error(f"Keywords error ({movie['id_tmdb']}): {type(e).__name__}: {e}")
            movie["keywords"] = ""

        # Image
        try:
            download_path = movie["poster_path"] or movie["backdrop_path"]
            if download_path:
                title = helper.clean_text(movie["title"])
                id_img = helper.clean_text(movie["id_tmdb"])
                img_name = f"{id_img}_{title}.jpg"
                movie["img_path"] = f"{INTERNAL_IMG_SAVE_PATH}{img_name}"
                client.get_img(download_path, img_name)
            else:
                movie["img_path"] = None
        except Exception as e:
            logging.error(f"Image error ({movie['id_tmdb']}): {type(e).__name__}: {e}")
            movie["img_path"] = None

        # All actors
        try:
            movie["all_actors"] = str(helper.get_all_actors(client, movie["id_tmdb"]))
        except Exception as e:
            logging.error(f"All actors error ({movie['id_tmdb']}): {type(e).__name__}: {e}")
            movie["all_actors"] = ""

        # Trailer
        try:
            movie["trailer_path"] = helper.get_videoMovie(client, movie["id_tmdb"], movie["original_language"])
        except Exception as e:
            logging.error(f"Trailer error ({movie['id_tmdb']}): {type(e).__name__}: {e}")
            movie["trailer_path"] = None

        # Insert movie + providers
        try:
            queries.insert_movie(cursor, movie)
            get_movie_providers(client, connection, cursor, movie["id_tmdb"])
        except Exception as e:
            logging.error(f"Insert Movie error ({movie['id_tmdb']}): {type(e).__name__}: {e}")


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

def get_languages(client, connection, cursor):
    param = endpoints.languages()
    response = client.get(endpoint=param["endpoint"], params=param["params"])

    languages = helper.extract_languages_list(response)

    for language in languages:
        try:
            queries.insert_language(cursor, language)
        except Exception as e:
            logging.error(f"Insert Language error ({language['code']}): {type(e).__name__}: {e}")

    connection.commit()

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

    #Get Regions and Providers (must run before movies so Movie_Providers can link correctly)
    get_regions(client, connection, cursor)
    get_providers(client, connection, cursor)

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

    get_languages(client, connection, cursor)
        

    cursor.close()
    connection.close()


