import logging
from tmdb.client import TMDBClient
from tmdb import endpoints, helper
from db.connection import get_connection
from db import queries
from config.settings import LOGO_IMG_PATH

def get_logo_provider(client, logo_path, provider_id, provider_name):
    if not logo_path:
        return None
    ext = logo_path.rsplit(".", 1)[-1]
    clean_name = helper.clean_text(f"{provider_id}_{provider_name}")
    img_name = f"{clean_name}.{ext}"
    client.get_img(logo_path, img_name, save_dir=LOGO_IMG_PATH)
    return f"Data/img_logo_providers/{img_name}"
    


def get_all_actors(client, connection, cursor, movie_id):
    param = endpoints.credits_movies(movie_id)
    response = client.get(endpoint=param["endpoint"], params=param["params"])

    cast = response.get("cast", [])
    if not cast:
        return []

    sorted_cast = sorted(cast, key=lambda x: x.get("order", 9999))
    return [member["name"] for member in sorted_cast[:20]]

def get_providers(client, connection, cursor):
    param = endpoints.watch_providers_movies()
    response = client.get(endpoint=param["endpoint"], params=param["params"])

    providers, provider_countries = helper.extract_providers_list(response)

    # Insert Providers
    for provider in providers:
        try:
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
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    client = TMDBClient()
    connection = get_connection()
    cursor = connection.cursor(buffered=True)
    movie_id = 1020414

    # get_regions(client, connection, cursor)
    # get_providers(client, connection, cursor)
    # get_movie_providers(client, connection, cursor, movie_id)

    # logo_path = "/SPnB1qiCkYfirS2it3hZORwGVn.jpg"
    # path = get_logo_provider(client, logo_path, provider_id=8, provider_name="Netflix")
    # print(path)

    get_languages(client, connection, cursor)

    cursor.close()
    connection.close()
