import json
import numpy as np

def insert_movie(cursor, movie):

    query = "INSERT INTO Movies (id_tmdb, adult, backdrop_path, original_lenguaje, overview, popularity, " \
        "                       poster_path, release_date, title, vote_average, vote_count, image_path, director, actors, keywords) " \
        "    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, 
                (movie["id_tmdb"], movie["adult"], movie["backdrop_path"], movie["original_lenguaje"], 
                    movie["overview"], movie["popularity"], movie["poster_path"], movie["release_date"], 
                    movie["title"], movie["vote_average"], movie["vote_count"], movie["img_path"], 
                    movie["director"], movie["actors"], movie["keywords"]))

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
    INSERT INTO Vectorized_Movies 
    (id, adult, original_lenguaje, title, keywords, popularity, 
     release_date, director, actors, vote_average, vote_count, gender, movie_vector) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    cursor.execute(query, (
        movie["id"],                    # ID es INT, no necesita conversión
        to_json(movie["adult"]),
        to_json(movie["original_lenguaje"]),
        to_json(movie["title"]),
        to_json(movie["keywords"]),
        to_json(movie["popularity"]),
        to_json(movie["release_date"]),
        to_json(movie["director"]),
        to_json(movie["actors"]),
        to_json(movie["vote_average"]),
        to_json(movie["vote_count"]),
        to_json(movie["gender"]),
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

def get_year_movies(cursor, year):
    query = "SELECT * FROM Movies WHERE YEAR(release_date) = %s"
    cursor.execute(query, (str(year),))
    results = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    return results, column_names