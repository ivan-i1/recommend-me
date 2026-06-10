import json
import numpy as np

def insert_movie(cursor, movie):

    query = "INSERT INTO Movies (id_tmdb, adult, backdrop_path, original_language, overview, popularity, " \
        "                       poster_path, release_date, title, vote_average, vote_count, image_path, director, " \
        "                       actors, keywords, trailer_path, all_actors) " \
        "    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, 
                (movie["id_tmdb"], movie["adult"], movie["backdrop_path"], movie["original_language"], 
                    movie["overview"], movie["popularity"], movie["poster_path"], movie["release_date"], 
                    movie["title"], movie["vote_average"], movie["vote_count"], movie["img_path"], 
                    movie["director"], movie["actors"], movie["keywords"], movie["trailer_path"], movie["all_actors"]))

def insert_genreMov(cursor, genreMov):
    query = "INSERT INTO GenreMov (id_genre_tmdb, name) VALUES (%s, %s)"
    cursor.execute(query, (genreMov["id_genre_tmdb"], genreMov["name"]))

def insert_movie_genres(cursor, movie_id, genres_id):
    query = "INSERT INTO Movie_Genres (movie_id, genre_id) VALUES (%s, %s)"
    cursor.execute(query, (movie_id, genres_id))

def insert_vectorized_movie(cursor, movie):
    # Función auxiliar para convertir cualquier valor a JSON
    def to_json(value):
        if value is None:
            return json.dumps(None)
        elif isinstance(value, (np.ndarray, list)):
            return json.dumps(value.tolist() if hasattr(value, 'tolist') else value)
        elif isinstance(value, (np.integer, int)):
            return json.dumps(int(value))
        elif isinstance(value, (np.floating, float)):
            return json.dumps(float(value))
        elif isinstance(value, str):
            return json.dumps(value)
        else:
            return json.dumps(str(value))
    
    query = """
    INSERT IGNORE INTO Vectorized_Movies
    (id, id_tmdb, adult, original_language, title, keywords, popularity,
     release_date, director, actors, vote_average, vote_count, genres, movie_vector)
    VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (
        movie["id"],
        movie["id_tmdb"],
        to_json(movie["adult"]),
        to_json(movie["original_language"]),
        to_json(movie["title"]),
        to_json(movie["keywords"]),
        to_json(movie["popularity"]),
        to_json(movie["release_date"]),
        to_json(movie["director"]),
        to_json(movie["actors"]),
        to_json(movie["vote_average"]),
        to_json(movie["vote_count"]),
        to_json(movie["genres"]),
        to_json(movie["movie_vector"])
    ))

def get_genreMov_id(cursor, id_genre_tmdb):
    query = "SELECT id FROM GenreMov WHERE id_genre_tmdb = %s"
    cursor.execute(query, (id_genre_tmdb,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_movie_id(cursor, id_tmdb):
    query = "SELECT id FROM Movies WHERE id_tmdb = %s"
    cursor.execute(query, (id_tmdb,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_gender_movie(cursor, movie_id):
    query = "SELECT genre_id FROM Movie_Genres Where movie_id = %s"
    cursor.execute(query, (str(movie_id),))
    results = cursor.fetchall()
    return [x[0] for x in results]

def insert_provider(cursor, provider):
    query = "INSERT IGNORE INTO Providers (tmdb_provider_id, name, logo_path) VALUES (%s, %s, %s)"
    cursor.execute(query, (provider["tmdb_provider_id"], provider["name"], provider["logo_path"]))

def get_provider_id(cursor, tmdb_provider_id):
    query = "SELECT id FROM Providers WHERE tmdb_provider_id = %s"
    cursor.execute(query, (tmdb_provider_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def insert_country(cursor, country):
    query = "INSERT INTO Countries (code, name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE name = VALUES(name)"
    cursor.execute(query, (country["code"], country["name"]))

def insert_language(cursor, language):
    query = "INSERT INTO Languages (code, english_name, native_name) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE english_name = VALUES(english_name), native_name = VALUES(native_name)"
    cursor.execute(query, (language["code"], language["english_name"], language["native_name"]))

def insert_country_if_not_exists(cursor, country_code):
    query = "INSERT IGNORE INTO Countries (code, name) VALUES (%s, %s)"
    cursor.execute(query, (country_code, country_code))

def insert_provider_country(cursor, provider_id, country_code, media_type, display_priority):
    query = "INSERT IGNORE INTO Provider_Countries (provider_id, country_code, media_type, display_priority) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (provider_id, country_code, media_type, display_priority))

def insert_movie_provider(cursor, movie_db_id, provider_db_id, country_code, provider_type, link=None):
    query = "INSERT IGNORE INTO Movie_Providers (movie_id, provider_id, country_code, provider_type, link) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (movie_db_id, provider_db_id, country_code, provider_type, link))

def get_movie_by_id(cursor, movie_id):
    query = "SELECT * FROM Movies WHERE id = %s"
    cursor.execute(query, (movie_id,))
    result = cursor.fetchone()
    column_names = [desc[0] for desc in cursor.description]
    return result, column_names

def get_latest_movie_date(cursor):
    query = "SELECT MAX(release_date) FROM Movies"
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0] if result and result[0] else None

def get_all_movie_tmdb_ids(cursor):
    query = "SELECT id_tmdb FROM Movies"
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]

def delete_movie_providers(cursor, movie_db_id):
    query = "DELETE FROM Movie_Providers WHERE movie_id = %s"
    cursor.execute(query, (movie_db_id,))

def get_year_movies(cursor, year):
    query = "SELECT * FROM Movies WHERE YEAR(release_date) = %s"
    cursor.execute(query, (str(year),))
    results = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    return results, column_names

def get_all_movies_actors(cursor):
    query = "SELECT id, all_actors, vote_count, vote_average FROM Movies WHERE all_actors IS NOT NULL AND all_actors != ''"
    cursor.execute(query)
    return cursor.fetchall()

def insert_actor(cursor, name, movie_count, total_votes, avg_rating, popularity_score):
    query = """
        INSERT INTO Actors (name, movie_count, total_votes, avg_rating, popularity_score)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            movie_count = VALUES(movie_count),
            total_votes = VALUES(total_votes),
            avg_rating = VALUES(avg_rating),
            popularity_score = VALUES(popularity_score)
    """
    cursor.execute(query, (name, movie_count, total_votes, avg_rating, popularity_score))

def get_actor_id(cursor, name):
    query = "SELECT id FROM Actors WHERE name = %s"
    cursor.execute(query, (name,))
    result = cursor.fetchone()
    return result[0] if result else None

def insert_movie_actor(cursor, movie_id, actor_id):
    query = "INSERT IGNORE INTO Movie_Actors (movie_id, actor_id) VALUES (%s, %s)"
    cursor.execute(query, (movie_id, actor_id))

def get_all_movies_directors(cursor):
    query = "SELECT id, director, vote_count, vote_average FROM Movies WHERE director IS NOT NULL AND director != ''"
    cursor.execute(query)
    return cursor.fetchall()

def insert_director(cursor, name, movie_count, total_votes, avg_rating, popularity_score):
    query = """
        INSERT INTO Directors (name, movie_count, total_votes, avg_rating, popularity_score)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            movie_count = VALUES(movie_count),
            total_votes = VALUES(total_votes),
            avg_rating = VALUES(avg_rating),
            popularity_score = VALUES(popularity_score)
    """
    cursor.execute(query, (name, movie_count, total_votes, avg_rating, popularity_score))

def get_director_id(cursor, name):
    query = "SELECT id FROM Directors WHERE name = %s"
    cursor.execute(query, (name,))
    result = cursor.fetchone()
    return result[0] if result else None

def insert_movie_director(cursor, movie_id, director_id):
    query = "INSERT IGNORE INTO Movie_Directors (movie_id, director_id) VALUES (%s, %s)"
    cursor.execute(query, (movie_id, director_id))

def get_new_movies_for_actors(cursor):
    query = """
        SELECT id, all_actors, vote_count, vote_average FROM Movies
        WHERE id NOT IN (SELECT DISTINCT movie_id FROM Movie_Actors)
        AND all_actors IS NOT NULL AND all_actors != ''
    """
    cursor.execute(query)
    return cursor.fetchall()

def get_new_movies_for_directors(cursor):
    query = """
        SELECT id, director, vote_count, vote_average FROM Movies
        WHERE id NOT IN (SELECT DISTINCT movie_id FROM Movie_Directors)
        AND director IS NOT NULL AND director != ''
    """
    cursor.execute(query)
    return cursor.fetchall()

def get_actor_stats_from_movies(cursor, actor_id):
    query = """
        SELECT COUNT(*) as movie_count, SUM(m.vote_count) as total_votes, AVG(m.vote_average) as avg_rating
        FROM Movie_Actors ma
        JOIN Movies m ON ma.movie_id = m.id
        WHERE ma.actor_id = %s
    """
    cursor.execute(query, (actor_id,))
    return cursor.fetchone()

def get_director_stats_from_movies(cursor, director_id):
    query = """
        SELECT COUNT(*) as movie_count, SUM(m.vote_count) as total_votes, AVG(m.vote_average) as avg_rating
        FROM Movie_Directors md
        JOIN Movies m ON md.movie_id = m.id
        WHERE md.director_id = %s
    """
    cursor.execute(query, (director_id,))
    return cursor.fetchone()

def update_actor_stats(cursor, actor_id, movie_count, total_votes, avg_rating, popularity_score):
    query = """
        UPDATE Actors SET movie_count = %s, total_votes = %s, avg_rating = %s, popularity_score = %s
        WHERE id = %s
    """
    cursor.execute(query, (movie_count, total_votes, avg_rating, popularity_score, actor_id))

def update_director_stats(cursor, director_id, movie_count, total_votes, avg_rating, popularity_score):
    query = """
        UPDATE Directors SET movie_count = %s, total_votes = %s, avg_rating = %s, popularity_score = %s
        WHERE id = %s
    """
    cursor.execute(query, (movie_count, total_votes, avg_rating, popularity_score, director_id))