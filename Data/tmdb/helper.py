

def extract_movies_list(response_json):

    for movie in response_json["results"]:
        print(movie)
    return response_json.get("results", [])



