import json

class Movie:
    def __init__(self, data: dict):
        self.id_tmdb = data.get("id", "")
        self.adult = data.get("adult", "")
        self.backdrop_path = data.get("backdrop_path", "")
        self.original_lenguaje = data.get("original_language", "")
        self.overview = data.get("overview", "")
        self.popularity = data.get("popularity", "")
        self.poster_path = data.get("poster_path", "")
        self.release_date = data.get("release_date", "")
        self.title = data.get("title", "")
        self.vote_average = data.get("vote_average", "")
        self.vote_count = data.get("vote_count", "")
        self.img_path = ""

    def to_json(self):
        return {
            "id_tmdb": self.id_tmdb,
            "adult": self.adult,
            "backdrop_path": self.backdrop_path,
            "original_lenguaje": self.original_lenguaje,
            "overview": self.overview,
            "popularity": self.popularity,
            "poster_path": self.poster_path,
            "release_date": self.release_date,
            "title": self.title,
            "vote_average": self.vote_average,
            "vote_count": self.vote_count,
            "img_path": self.img_path
        }