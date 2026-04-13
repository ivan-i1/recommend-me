import os

TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"
TIMEOUT = 60

#PERIOD DATE EXTRACTION
START_DATE_EXTRACTION = "2020-01-01"
END_DATE_EXTRACTION = "2020-03-01"

#IMAGE PATH
BASE_IMG_URL = "https://image.tmdb.org/t/p/w500"
POSTER_IMG_PATH = os.environ.get("POSTER_IMG_PATH")
INTERNAL_IMG_SAVE_PATH = os.environ.get("INTERNAL_IMG_SAVE_PATH")

#CONECTION DB
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_USER = os.environ.get("MYSQL_USER")
DB_PASWORD = os.environ.get("MYSQL_PASSWORD")
DB_NAME = os.environ.get("MYSQL_DATABASE")

#MOVIE WIGHTS
w_adult = 2
w_original_lenguaje = 4
w_title = 3
w_keywords = 5
w_popularity = 3
w_date = 3
w_director = 5
w_actors = 5
w_vote_average = 3
w_vote_count = 3
w_Genre = 7

#TOTAL WIGHTS
TOTAL_WIGHT = 43
