import logging
from tmdb.client import TMDBClient
from tmdb import endpoints, helper
from db.connection import get_connection
from db import queries

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

def update_movie_providers(client, connection, cursor):
    tmdb_ids = queries.get_all_movie_tmdb_ids(cursor)
    logging.info(f"Starting Movie_Providers update for {len(tmdb_ids)} movies.")

    for tmdb_movie_id in tmdb_ids:
        try:
            movie_db_id = queries.get_movie_id(cursor, tmdb_movie_id)
            if movie_db_id is None:
                logging.warning(f"Movie {tmdb_movie_id} not found in DB, skipping.")
                continue

            param = endpoints.movie_watch_providers(tmdb_movie_id)
            response = client.get(endpoint=param["endpoint"], params=param["params"])
            entries = helper.extract_movie_providers_list(response)

            # Atomic: delete old + insert new in one transaction
            queries.delete_movie_providers(cursor, movie_db_id)

            for entry in entries:
                try:
                    provider_db_id = queries.get_provider_id(cursor, entry["tmdb_provider_id"])
                    if provider_db_id is None:
                        logging.warning(f"Provider {entry['tmdb_provider_id']} not in DB, skipping.")
                        continue
                    queries.insert_movie_provider(
                        cursor,
                        movie_db_id,
                        provider_db_id,
                        entry["country_code"],
                        entry["provider_type"],
                        entry.get("link")
                    )
                except Exception as e:
                    logging.error(f"Insert MovieProvider error ({tmdb_movie_id} - {entry}): {type(e).__name__}: {e}")

            connection.commit()
            logging.info(f"Updated Movie_Providers for tmdb_id={tmdb_movie_id} ({len(entries)} entries).")

        except Exception as e:
            connection.rollback()
            logging.error(f"Update MovieProviders error (tmdb_id={tmdb_movie_id}): {type(e).__name__}: {e}")

    logging.info("Movie_Providers update complete.")


if __name__ == "__main__":

    logging.basicConfig(
        filename="/app/logs/app.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
        )

    client = TMDBClient()
    connection = get_connection()
    cursor = connection.cursor(buffered=True)

    update_movie_providers(client, connection, cursor)

    cursor.close()
    connection.close()