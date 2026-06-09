from rest_framework import serializers
from ..models import Movies, Vectorized_Movies, MovieGenres, MovieProviders, Countries
import json
import os

class MovieSerializer(serializers.ModelSerializer):

    vector = serializers.SerializerMethodField()
    genres = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    providers = serializers.SerializerMethodField()

    class Meta:
        model = Movies
        fields = ['id', 'id_tmdb', 'adult', 'original_language',
                  'overview', 'release_date', 'title', 'genres', 'director',
                  'actors', 'vote_average', 'vote_count', 'image_url', 'trailer_path',
                  'providers', 'vector']

    def get_vector(self, obj):
        vectorized_movie = Vectorized_Movies.objects.get(id=obj.id)
        return vectorized_movie.movie_vector

    def get_genres(self, obj):
        movie_genres = MovieGenres.objects.filter(movie=obj)
        return [{"id": mg.genre.id, "name": mg.genre.name} for mg in movie_genres]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if not obj.image_path:
            return None
        filename = os.path.basename(obj.image_path)
        return request.build_absolute_uri(f"/media/{filename}")

    def get_providers(self, obj):
        request = self.context.get("request")
        if not request:
            return []
        country_code = request.query_params.get("country_code") or request.data.get("country_code")
        if not country_code:
            return []

        entries = MovieProviders.objects.filter(
            movie=obj, country=country_code
        ).values(
            'provider_id',
            'provider__name',
            'provider__logo_path',
            'link',
        ).order_by('provider_id')

        seen = set()
        result = []
        for entry in entries:
            pid = entry['provider_id']
            if pid not in seen:
                seen.add(pid)
                logo_url = None
                if entry['provider__logo_path']:
                    filename = os.path.basename(entry['provider__logo_path'])
                    logo_url = request.build_absolute_uri(f"/logos/{filename}")
                result.append({
                    'id': pid,
                    'name': entry['provider__name'],
                    'logo_url': logo_url,
                    'link': entry['link'],
                })

        if not result:
            try:
                country_name = Countries.objects.get(code=country_code).name
            except Countries.DoesNotExist:
                country_name = country_code
            return f"This movie is not available on any streaming platform in {country_name}"

        return result

    

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