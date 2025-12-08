import logging
from tmdb.client import TMDBClient
from tmdb import endpoints


logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

client = TMDBClient()

call = endpoints.discover_movies(10,"2020-02-01", "2020-02-01")
response = client.get(
        endpoint=call["endpoint"], 
        params = call["params"]
    )




print(response)