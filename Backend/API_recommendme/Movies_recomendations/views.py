from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from .models import Movies
from .serializers import MovieSerializer


class MoviesViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Movies.objects.all()
    serializer_class = MovieSerializer

    @action(detail=False, methods=['get'])
    def two_options(self, request):
        response = {
            "message": "Hello World!!"
        }
        return Response(response, status=status.HTTP_200_OK)