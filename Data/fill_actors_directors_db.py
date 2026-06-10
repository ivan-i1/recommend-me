import logging
import ast
import math
from db.connection import get_connection
from db import queries


def parse_actors(all_actors_str):
    try:
        return ast.literal_eval(all_actors_str)
    except Exception:
        return []


def calculate_popularity(movie_count, total_votes, avg_rating):
    return round(movie_count * avg_rating * math.log10(total_votes + 1), 3)


def fill_actors(connection, cursor):
    logging.info("Reading movies for actors...")
    movies = queries.get_all_movies_actors(cursor)
    logging.info(f"Found {len(movies)} movies with actors.")

    actor_stats = {}
    for movie_id, all_actors_str, vote_count, vote_average in movies:
        actors = parse_actors(all_actors_str)
        vote_count = vote_count or 0
        vote_average = float(vote_average) if vote_average else 0.0

        for name in actors:
            name = name.strip()
            if not name:
                continue
            if name not in actor_stats:
                actor_stats[name] = {"movie_ids": [], "total_votes": 0, "rating_sum": 0.0}
            actor_stats[name]["movie_ids"].append(movie_id)
            actor_stats[name]["total_votes"] += vote_count
            actor_stats[name]["rating_sum"] += vote_average

    logging.info(f"Found {len(actor_stats)} unique actors.")

    for name, stats in actor_stats.items():
        movie_count = len(stats["movie_ids"])
        total_votes = stats["total_votes"]
        avg_rating = round(stats["rating_sum"] / movie_count, 3)
        popularity_score = calculate_popularity(movie_count, total_votes, avg_rating)
        try:
            queries.insert_actor(cursor, name, movie_count, total_votes, avg_rating, popularity_score)
        except Exception as e:
            logging.error(f"Insert Actor error ({name}): {type(e).__name__}: {e}")

    connection.commit()
    logging.info("Actors inserted.")

    for name, stats in actor_stats.items():
        try:
            actor_id = queries.get_actor_id(cursor, name)
            if actor_id is None:
                logging.warning(f"Actor '{name}' not found in DB, skipping.")
                continue
            for movie_id in stats["movie_ids"]:
                try:
                    queries.insert_movie_actor(cursor, movie_id, actor_id)
                except Exception as e:
                    logging.error(f"Insert Movie_Actor error ({name} - movie {movie_id}): {type(e).__name__}: {e}")
        except Exception as e:
            logging.error(f"Movie_Actor loop error ({name}): {type(e).__name__}: {e}")

    connection.commit()
    logging.info("Movie_Actors inserted.")


def fill_directors(connection, cursor):
    logging.info("Reading movies for directors...")
    movies = queries.get_all_movies_directors(cursor)
    logging.info(f"Found {len(movies)} movies with directors.")

    director_stats = {}
    for movie_id, director_str, vote_count, vote_average in movies:
        name = director_str.strip() if director_str else ""
        if not name:
            continue
        vote_count = vote_count or 0
        vote_average = float(vote_average) if vote_average else 0.0

        if name not in director_stats:
            director_stats[name] = {"movie_ids": [], "total_votes": 0, "rating_sum": 0.0}
        director_stats[name]["movie_ids"].append(movie_id)
        director_stats[name]["total_votes"] += vote_count
        director_stats[name]["rating_sum"] += vote_average

    logging.info(f"Found {len(director_stats)} unique directors.")

    for name, stats in director_stats.items():
        movie_count = len(stats["movie_ids"])
        total_votes = stats["total_votes"]
        avg_rating = round(stats["rating_sum"] / movie_count, 3)
        popularity_score = calculate_popularity(movie_count, total_votes, avg_rating)
        try:
            queries.insert_director(cursor, name, movie_count, total_votes, avg_rating, popularity_score)
        except Exception as e:
            logging.error(f"Insert Director error ({name}): {type(e).__name__}: {e}")

    connection.commit()
    logging.info("Directors inserted.")

    for name, stats in director_stats.items():
        try:
            director_id = queries.get_director_id(cursor, name)
            if director_id is None:
                logging.warning(f"Director '{name}' not found in DB, skipping.")
                continue
            for movie_id in stats["movie_ids"]:
                try:
                    queries.insert_movie_director(cursor, movie_id, director_id)
                except Exception as e:
                    logging.error(f"Insert Movie_Director error ({name} - movie {movie_id}): {type(e).__name__}: {e}")
        except Exception as e:
            logging.error(f"Movie_Director loop error ({name}): {type(e).__name__}: {e}")

    connection.commit()
    logging.info("Movie_Directors inserted.")


if __name__ == "__main__":
    logging.basicConfig(
        filename="/app/logs/app.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    connection = get_connection()
    cursor = connection.cursor(buffered=True)

    fill_actors(connection, cursor)
    fill_directors(connection, cursor)

    cursor.close()
    connection.close()
    logging.info("fill_actors_directors_db.py completed.")
