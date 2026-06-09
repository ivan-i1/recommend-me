def discover_movies(page, start_date, end_date):
    return {
        "endpoint": "discover/movie",
        "params": {
            "page": page,
            "primary_release_date.gte": start_date,
            "primary_release_date.lte": end_date,
        }
    }

def movie_genres():
    return {
        "endpoint": "genre/movie/list",
        "params": {}
    }

def credits_movies(movie_id):
    return {
        "endpoint": f"movie/{movie_id}/credits",
        "params": {}
    }

def videos_movies(movie_id, language="en-US"):
    return {
        "endpoint": f"movie/{movie_id}/videos",
        "params": {
            "language": language
        }
    }

def watch_providers_movies(language="en-US"):
    return {
        "endpoint": "watch/providers/movie",
        "params": {
            "language": language,
        }
    }

def watch_provider_regions(language="en-US"):
    return {
        "endpoint": "watch/providers/regions",
        "params": {
            "language": language
        }
    }

def movie_watch_providers(movie_id):
    return {
        "endpoint": f"movie/{movie_id}/watch/providers",
        "params": {}
    }

def languages():
    return {
        "endpoint": "configuration/languages",
        "params": {}
    }