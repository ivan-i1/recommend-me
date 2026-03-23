from rest_framework import serializers
from ..models import Genremov

class GenreMovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genremov   
        fields = ['id','name'] 