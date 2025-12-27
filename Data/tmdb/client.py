import requests
import logging
from config.settings import TMDB_API_KEY, BASE_URL, TIMEOUT, BASE_IMG_URL, POSTER_IMG_PATH

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

    def get_img(self,poster_path, img_name):
        img_save_path = f"{POSTER_IMG_PATH}{img_name}"
        url = f"{BASE_IMG_URL}{poster_path}"

        logging.info(f"GET_IMG {url}")

        try:
            response = requests.get(url)
            response.raise_for_status()
            with open(img_save_path, "wb") as f:
                f.write(response.content)

        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP error: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error: {e}")
            raise
