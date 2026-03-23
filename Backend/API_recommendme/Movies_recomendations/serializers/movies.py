from rest_framework import serializers
from ..models import Movies, Vectorized_Movies

class MovieSerializer(serializers.ModelSerializer):

    vector = serializers.SerializerMethodField()
    
    class Meta:
        model = Movies   
        fields = ['id', 'id_tmdb', 'adult', 'original_lenguaje', 
                  'overview', 'release_date', 'title', 'director', 
                  'actors', 'vote_average', 'vote_count', 'image_path', 'vector']

    def get_vector(self, obj):
        vectorized_movie = Vectorized_Movies.objects.get(id=obj.id)
        return vectorized_movie.movie_vector