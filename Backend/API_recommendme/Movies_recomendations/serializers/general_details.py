from rest_framework import serializers
from ..models import Genremov, Countries, Providers
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


class ValidRequestSerializer(serializers.Serializer):
    def validate(self, attrs):
        if self.context['request'].query_params:
            raise serializers.ValidationError(
                "This endpoint does not accept query parameters."
            )
        return attrs
    
