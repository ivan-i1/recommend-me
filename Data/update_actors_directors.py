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


def update_actors(connection, cursor):
    new_movies = queries.get_new_movies_for_actors(cursor)
    if not new_movies:
        logging.info("No new movies to process for actors.")
        return

    logging.info(f"Found {len(new_movies)} new movies to process for actors.")

    # Map actor_name -> [movie_ids] for the new movies only
    new_actor_movies = {}
    for movie_id, all_actors_str, _, _ in new_movies:
        for name in parse_actors(all_actors_str):
            name = name.strip()
            if not name:
                continue
            if name not in new_actor_movies:
                new_actor_movies[name] = []
            new_actor_movies[name].append(movie_id)

    logging.info(f"Identified {len(new_actor_movies)} actors in new movies.")

    # Insert actors that don't exist yet (stats will be updated later)
    new_actors_count = 0
    for name in new_actor_movies:
        if queries.get_actor_id(cursor, name) is None:
            queries.insert_actor(cursor, name, 0, 0, 0.0, 0.0)
            new_actors_count += 1

    connection.commit()
    logging.info(f"Inserted {new_actors_count} new actors.")

    # Link actors to new movies
    linked = 0
    for name, movie_ids in new_actor_movies.items():
        actor_id = queries.get_actor_id(cursor, name)
        if actor_id is None:
            logging.warning(f"Actor '{name}' not found after insert, skipping.")
            continue
        for movie_id in movie_ids:
            try:
                queries.insert_movie_actor(cursor, movie_id, actor_id)
                linked += 1
            except Exception as e:
                logging.error(f"Movie_Actor insert error ({name} - movie {movie_id}): {e}")

    connection.commit()
    logging.info(f"Inserted {linked} Movie_Actor links.")

    # Recalculate stats for all affected actors using DB (includes all their movies, not just new ones)
    updated = 0
    for name in new_actor_movies:
        actor_id = queries.get_actor_id(cursor, name)
        if actor_id is None:
            continue
        row = queries.get_actor_stats_from_movies(cursor, actor_id)
        if row:
            movie_count = row[0] or 0
            total_votes = int(row[1]) if row[1] else 0
            avg_rating = round(float(row[2]), 3) if row[2] else 0.0
            popularity_score = calculate_popularity(movie_count, total_votes, avg_rating)
            queries.update_actor_stats(cursor, actor_id, movie_count, total_votes, avg_rating, popularity_score)
            updated += 1

    connection.commit()
    logging.info(f"Updated stats for {updated} actors.")


def update_directors(connection, cursor):
    new_movies = queries.get_new_movies_for_directors(cursor)
    if not new_movies:
        logging.info("No new movies to process for directors.")
        return

    logging.info(f"Found {len(new_movies)} new movies to process for directors.")

    # Map director_name -> [movie_ids] for the new movies only
    new_director_movies = {}
    for movie_id, director_str, _, _ in new_movies:
        name = director_str.strip() if director_str else ""
        if not name:
            continue
        if name not in new_director_movies:
            new_director_movies[name] = []
        new_director_movies[name].append(movie_id)

    logging.info(f"Identified {len(new_director_movies)} directors in new movies.")

    # Insert directors that don't exist yet
    new_directors_count = 0
    for name in new_director_movies:
        if queries.get_director_id(cursor, name) is None:
            queries.insert_director(cursor, name, 0, 0, 0.0, 0.0)
            new_directors_count += 1

    connection.commit()
    logging.info(f"Inserted {new_directors_count} new directors.")

    # Link directors to new movies
    linked = 0
    for name, movie_ids in new_director_movies.items():
        director_id = queries.get_director_id(cursor, name)
        if director_id is None:
            logging.warning(f"Director '{name}' not found after insert, skipping.")
            continue
        for movie_id in movie_ids:
            try:
                queries.insert_movie_director(cursor, movie_id, director_id)
                linked += 1
            except Exception as e:
                logging.error(f"Movie_Director insert error ({name} - movie {movie_id}): {e}")

    connection.commit()
    logging.info(f"Inserted {linked} Movie_Director links.")

    # Recalculate stats for all affected directors using DB
    updated = 0
    for name in new_director_movies:
        director_id = queries.get_director_id(cursor, name)
        if director_id is None:
            continue
        row = queries.get_director_stats_from_movies(cursor, director_id)
        if row:
            movie_count = row[0] or 0
            total_votes = int(row[1]) if row[1] else 0
            avg_rating = round(float(row[2]), 3) if row[2] else 0.0
            popularity_score = calculate_popularity(movie_count, total_votes, avg_rating)
            queries.update_director_stats(cursor, director_id, movie_count, total_votes, avg_rating, popularity_score)
            updated += 1

    connection.commit()
    logging.info(f"Updated stats for {updated} directors.")


if __name__ == "__main__":
    logging.basicConfig(
        filename="/app/logs/app.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    connection = get_connection()
    cursor = connection.cursor(buffered=True)

    update_actors(connection, cursor)
    update_directors(connection, cursor)

    cursor.close()
    connection.close()
    logging.info("update_actors_directors.py completed.")
