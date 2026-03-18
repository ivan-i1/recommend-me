from rest_framework import serializers
from ..models import Movies

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movies   
        fields = ['id', 'id_tmdb', 'adult', 'original_lenguaje', 
                  'overview', 'release_date', 'title', 'director', 
                  'actors', 'vote_average', 'vote_count', 'image_path']