import logging
import time
import pandas as pd
from datetime import date, timedelta
from config.settings import INTERNAL_IMG_SAVE_PATH
from tmdb.client import TMDBClient
from tmdb import endpoints, helper
from db.connection import get_connection
from db import queries
from vectorized_db import v_helpers
from fill_movie_db import get_movie_providers


def get_movies(client, connection, cursor, date_str, page):
    paramMov = endpoints.discover_movies(page, date_str, date_str)
    response = client.get(endpoint=paramMov["endpoint"], params=paramMov["params"])

    json_movies, movie_genre_json = helper.extract_movies_list(response)

    for movie in json_movies:
        try:
            # Get Actors and Director
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
                movie["director"] = str(director["name"].values[0])
            else:
                movie["director"] = ""

            # Get keywords
            movie["keywords"] = helper.extract_keywords(str(movie["overview"]))

            # Get Images
            download_path = movie["poster_path"] if movie["poster_path"] is not None else movie["backdrop_path"]
            title = helper.clean_text(movie["title"])
            id_img = helper.clean_text(movie["id_tmdb"])
            img_name = id_img + "_" + title + ".jpg"
            img_path = f"{INTERNAL_IMG_SAVE_PATH}{img_name}"

            if download_path is not None:
                movie["img_path"] = img_path
                client.get_img(download_path, img_name)

            # Get all actors
            movie["all_actors"] = str(helper.get_all_actors(client, movie["id_tmdb"]))

            # Get Trailer
            movie["trailer_path"] = helper.get_videoMovie(client, movie["id_tmdb"], movie["original_language"])

            # Insert Movie
            queries.insert_movie(cursor, movie)
            connection.commit()

            # Insert Providers
            get_movie_providers(client, connection, cursor, movie["id_tmdb"])

            # Vectorize immediately after insert
            movie_db_id = queries.get_movie_id(cursor, movie["id_tmdb"])
            if movie_db_id:
                result, col_names = queries.get_movie_by_id(cursor, movie_db_id)
                if result:
                    df = pd.DataFrame([result], columns=col_names)
                    df_vec = v_helpers.movie_vectorized_table(cursor, df)
                    for _, vec_row in df_vec.iterrows():
                        try:
                            queries.insert_vectorized_movie(cursor, vec_row)
                        except Exception as e:
                            logging.error(f"Insert Vectorized Movie error ({movie['id_tmdb']}): {type(e).__name__}: {e}")
                    connection.commit()

        except Exception as e:
            logging.error(f"Insert Movie error: {type(e).__name__}: {e}")

    # Insert Movie_Genres
    for movie_id in movie_genre_json:
        try:
            id_mov = queries.get_movie_id(cursor, movie_id)
            for genre in movie_genre_json[movie_id]:
                id_gen = queries.get_genreMov_id(cursor, genre)
                queries.insert_movie_genres(cursor, id_mov, id_gen)
        except Exception as e:
            logging.error(f"Insert Movie_Genre error: {type(e).__name__}: {e}")

    connection.commit()
    return response["total_pages"]


if __name__ == "__main__":

    logging.basicConfig(
        filename="/app/logs/app.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    client = TMDBClient()
    connection = get_connection()
    cursor = connection.cursor(buffered=True)

    latest_date = queries.get_latest_movie_date(cursor)
    if latest_date is None:
        logging.error("No movies found in DB. Run fill_movie_db.py first.")
        cursor.close()
        connection.close()
        exit(1)

    start_date = (latest_date + timedelta(days=1)).strftime("%Y-%m-%d")
    end_date = date.today().strftime("%Y-%m-%d")

    logging.info(f"Adding new movies from {start_date} to {end_date}.")

    if start_date > end_date:
        logging.info("DB is already up to date. No new movies to add.")
        cursor.close()
        connection.close()
        exit(0)

    dateList = helper.generate_dateList(start_date, end_date)

    for year in dateList:
        for date_str in dateList[year]:
            try:
                page = 1
                pageNum = get_movies(client, connection, cursor, date_str, page)
                page += 1
                while page <= pageNum:
                    get_movies(client, connection, cursor, date_str, page)
                    page += 1
            except Exception as e:
                logging.error(f"Loop Insert Movie error: {type(e).__name__}: {e}")
                time.sleep(60)
                continue

    cursor.close()
    connection.close()
