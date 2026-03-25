from rest_framework import serializers
from ..models import Movies, Vectorized_Movies
import json

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

class startMoviesRequestSerializer(serializers.Serializer):

    genres = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        allow_empty=True
    )
    min_year = serializers.IntegerField(required=True)
    max_year = serializers.IntegerField(required=True)
    adult = serializers.BooleanField(required=True)


    def validate(self, attrs):
        min_year = attrs["min_year"]
        max_year = attrs["max_year"]
        genres = attrs["genres"]

        if min_year > max_year:
            raise serializers.ValidationError({
                "max_year": "max_year should be bigger than min_year."
            })

        return attrs

class DetailsRequestSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )

class TwoOptionsRequestSerializer(serializers.Serializer):
    vector = serializers.ListField(
        child=serializers.FloatField(),
        required=True,
        allow_empty=False,
        min_length=43,
        max_length=43
    )
    genres = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    min_year = serializers.IntegerField(required=True)
    max_year = serializers.IntegerField(required=True)
    adult = serializers.BooleanField(required=True)

    ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )

    def validate(self, attrs):
        min_year = attrs.get("min_year")
        max_year = attrs.get("max_year")

        if min_year > max_year:
            raise serializers.ValidationError({
                "max_year": "max_year should be bigger than min_year."
            })

        return attrs