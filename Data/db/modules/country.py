class Country:
    def __init__(self, data: dict):
        self.code = data.get("iso_3166_1", "")
        self.name = data.get("english_name", "")

    def to_json(self):
        return {
            "code": self.code,
            "name": self.name
        }
