from db.modules.movie import Movie
from db.modules.genreMov import GenreMov
from db.modules.provider import Provider
from db.modules.country import Country
from datetime import datetime, timedelta
from config.settings import POSTER_IMG_PATH, LOGO_IMG_PATH
import requests
import re
from keybert import KeyBERT
from tmdb import endpoints, helper



def extract_movies_list(response_json):
    movie_jsons = []
    movie_genre_json = {}

    for item in response_json["results"]:
        if item['popularity'] >= 1 and item['vote_average'] >= 3 and item['vote_count'] >= 50:
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
    
    year_dict = {}
    current_date = start
    
    while current_date <= end:
        year_key = current_date.strftime("%Y")
        
        if year_key not in year_dict:
            year_dict[year_key] = []
            
        year_dict[year_key].append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    
    return year_dict

_kw_model = None

def extract_keywords(text, n=4):
    global _kw_model
    if _kw_model is None:
        _kw_model = KeyBERT()

    keywords = _kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words='english',
        top_n=n,
        use_mmr=True,
        diversity=0.5
    )

    return str([word for word, sim in keywords])

def get_videoMovie(client, movie_id, original_language=None):
    def fetch_videos(language):
        param = endpoints.videos_movies(movie_id, language=language)
        response = client.get(endpoint=param["endpoint"], params=param["params"])
        return response.get("results", [])

    def find_trailer(results):
        return next((v for v in results if v.get("type") == "Trailer" and v.get("site") == "YouTube"), None)

    def find_any_video(results):
        return next((v for v in results if v.get("site") == "YouTube"), None)

    def to_url(video):
        return f"https://www.youtube.com/watch?v={video['key']}"

    # 1. Trailer en inglés
    en_results = fetch_videos("en-US")
    trailer = find_trailer(en_results)
    if trailer:
        return to_url(trailer)

    # 2. Trailer en idioma original
    if original_language and original_language != "en":
        lang_code = f"{original_language}-{original_language.upper()}"
        orig_results = fetch_videos(lang_code)
        trailer = find_trailer(orig_results)
        if trailer:
            return to_url(trailer)

        # 3. Cualquier video en idioma original (Teaser, Clip, etc.)
        video = find_any_video(orig_results)
        if video:
            return to_url(video)

    # 4. Cualquier video en inglés
    video = find_any_video(en_results)
    if video:
        return to_url(video)

    return None

def extract_providers_list(response_json):
    providers = []
    provider_countries = {}

    for item in response_json.get("results", []):
        provider = Provider(item)
        providers.append(provider.to_json())

        tmdb_id = item["provider_id"]
        provider_countries[tmdb_id] = [
            {"country_code": code, "display_priority": priority}
            for code, priority in item.get("display_priorities", {}).items()
        ]

    return providers, provider_countries

def extract_countries_list(response_json):
    return [Country(item).to_json() for item in response_json.get("results", [])]

def extract_languages_list(response_json):
    return [
        {
            "code": item.get("iso_639_1"),
            "english_name": item.get("english_name"),
            "native_name": item.get("name"),
        }
        for item in response_json
        if item.get("iso_639_1")
    ]

_PROVIDER_TYPES = ['flatrate', 'rent', 'buy', 'free', 'ads']

def extract_movie_providers_list(response_json):
    entries = []
    for country_code, country_data in response_json.get("results", {}).items():
        link = country_data.get("link")
        for provider_type in _PROVIDER_TYPES:
            for provider in country_data.get(provider_type, []):
                entries.append({
                    "country_code": country_code,
                    "tmdb_provider_id": provider.get("provider_id"),
                    "provider_type": provider_type,
                    "link": link
                })
    return entries

def get_all_actors(client, movie_id):
    param = endpoints.credits_movies(movie_id)
    response = client.get(endpoint=param["endpoint"], params=param["params"])

    cast = response.get("cast", [])
    if not cast:
        return []

    sorted_cast = sorted(cast, key=lambda x: x.get("order", 9999))
    return [member["name"] for member in sorted_cast[:20]]

def get_logo_provider(client, logo_path, provider_id, provider_name):
    if not logo_path:
        return None
    ext = logo_path.rsplit(".", 1)[-1]
    clean_name = helper.clean_text(f"{provider_id}_{provider_name}")
    img_name = f"{clean_name}.{ext}"
    client.get_img(logo_path, img_name, save_dir=LOGO_IMG_PATH)
    return f"Data/img_logo_providers/{img_name}"