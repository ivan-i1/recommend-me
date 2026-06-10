from rest_framework import serializers
from ..models import Genremov, Countries, Providers, Languages, Actors, MovieActors, Directors, MovieDirectors
import os

class GenreMovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genremov
        fields = ['id','name']

class ProvidersSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Providers
        fields = ['id', 'tmdb_provider_id', 'name', 'logo_url', 'website_url']

    def get_logo_url(self, obj):
        request = self.context.get("request")
        if not obj.logo_path:
            return None
        filename = os.path.basename(obj.logo_path)
        return request.build_absolute_uri(f"/logos/{filename}")


class CountriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Countries
        fields = ['code', 'name']


class LanguagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Languages
        fields = ['code', 'english_name', 'native_name']


class ActorSerializer(serializers.ModelSerializer):
    movies = serializers.SerializerMethodField()

    class Meta:
        model = Actors
        fields = ['id', 'name', 'movie_count', 'popularity_score', 'movies']

    def get_movies(self, obj):
        return list(
            MovieActors.objects
            .filter(actor=obj)
            .values('movie__id', 'movie__title')
            .order_by('movie__release_date')
        )


class DirectorSerializer(serializers.ModelSerializer):
    movies = serializers.SerializerMethodField()

    class Meta:
        model = Directors
        fields = ['id', 'name', 'movie_count', 'popularity_score', 'movies']

    def get_movies(self, obj):
        return list(
            MovieDirectors.objects
            .filter(director=obj)
            .values('movie__id', 'movie__title')
            .order_by('movie__release_date')
        )


class ValidRequestSerializer(serializers.Serializer):
    def validate(self, attrs):
        if self.context['request'].query_params:
            raise serializers.ValidationError(
                "This endpoint does not accept query parameters."
            )
        return attrs
    
