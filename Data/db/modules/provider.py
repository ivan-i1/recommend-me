class Provider:
    def __init__(self, data: dict):
        self.tmdb_provider_id = data.get("provider_id", "")
        self.name = data.get("provider_name", "")
        self.logo_path = data.get("logo_path", "")

    def to_json(self):
        return {
            "tmdb_provider_id": self.tmdb_provider_id,
            "name": self.name,
            "logo_path": self.logo_path
        }
