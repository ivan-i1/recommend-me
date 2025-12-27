from db.modules.movie import Movie
from db.modules.genreMov import GenreMov
from datetime import datetime, timedelta
from config.settings import POSTER_IMG_PATH
import requests
import re



def extract_movies_list(response_json):
    movie_jsons = []
    movie_genre_json = {}

    for item in response_json["results"]:
        movie = Movie(item)
        movie_jsons.append(movie.to_json())
        movie_genre_json[item['id']] = item["genre_ids"]
    return movie_jsons, movie_genre_json

def extract_genreMov_list(response_json):
    genreMov_jsons = []

    for item in response_json["genres"]:
        genreMov = GenreMov(item)
        genreMov_jsons.append(genreMov.to_json())
    return genreMov_jsons

def clean_text(text):
    text = str(text).lower().strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-z0-9\s\-]', '', text)
    text = text.replace(' ', '_')
    text = re.sub(r'_+', '_', text)
    
    return str(text)

def generate_dateList(start_date: str, end_date: str):

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    dateList = []

    while start <= end:
        dateList.append(start.strftime("%Y-%m-%d"))
        start += timedelta(days=1)

    return dateList