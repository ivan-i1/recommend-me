import json

class GenreMov:
    def __init__(self, data: dict):
        self.id_genre_tmdb = data.get("id", "")
        self.name = data.get("name", "")

    def to_json(self):
        return {
            "id_genre_tmdb": self.id_genre_tmdb,
            "name": self.name
        }