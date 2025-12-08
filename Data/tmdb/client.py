import requests
import logging
from config.settings import TMDB_API_KEY, BASE_URL, TIMEOUT

class TMDBClient:
    def __init__(self, api_key=TMDB_API_KEY):
        self.api_key = api_key

    def get(self, endpoint, params=None):

        if params is None:
            params = {}

        headers = {
            "accept": "application/json",
            "Authorization": "Bearer " + self.api_key,
            }

        url = f"{BASE_URL}/{endpoint}"

        logging.info(f"GET {url} - params={params}")

        try:
            response = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP error: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error: {e}")
            raise