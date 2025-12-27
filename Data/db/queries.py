
def insert_movie(cursor, movie):

    query = "INSERT INTO Movies (id_tmdb, adult, backdrop_path, original_lenguaje, overview, popularity, " \
        "                       poster_path, release_date, title, vote_average, vote_count, image_path) " \
        "    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, 
                (movie["id_tmdb"], movie["adult"], movie["backdrop_path"], movie["original_lenguaje"], 
                    movie["overview"], movie["popularity"], movie["poster_path"], movie["release_date"], 
                    movie["title"], movie["vote_average"], movie["vote_count"], movie["img_path"]))

def insert_genreMov(cursor, genreMov):
    query = "INSERT INTO GenreMov (id_genre_tmdb, name) VALUES (%s, %s)"
    cursor.execute(query, (genreMov["id_genre_tmdb"], genreMov["name"]))

def insert_movie_genres(cursor, movie_id, genres_id):
    query = "INSERT INTO Movie_Genres (movie_id, genre_id) VALUES (%s, %s)"
    cursor.execute(query, (movie_id, genres_id))

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
