def discover_movies(page, start_date, end_date):
    return {
        "endpoint": "discover/movie",
        "params": {
            "page": page,
            "primary_release_date.gte": start_date,
            "primary_release_date.lte": end_date,
        }
    }