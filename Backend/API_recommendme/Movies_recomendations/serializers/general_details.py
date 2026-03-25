from rest_framework import serializers
from ..models import Genremov

class GenreMovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genremov   
        fields = ['id','name'] 

class GenreRequestSerializer(serializers.Serializer):
    def validate(self, attrs):
        if self.context['request'].query_params:
            raise serializers.ValidationError(
                "This endpoint does not accept query parameters."
            )
        return attrs