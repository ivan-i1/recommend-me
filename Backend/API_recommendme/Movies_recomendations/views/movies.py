from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from ..models import Movies, Vectorized_Movies
from ..serializers.movies import MovieSerializer
from ..utils import get_distance_vectors
import numpy as np
import random


class MoviesViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Movies.objects.all()
    serializer_class = MovieSerializer

    @action(detail=False, methods=['post'])
    def two_options(self, request):

        #Get vector from request
        body_data = request.data
        query_vector = body_data['vector']

        #Filter Movies by id's
        genres = body_data['genres']
        min_year = body_data['min_year']
        max_year = body_data['max_year']
        adult = body_data['adult']
        query_id = body_data['id']

        movies = self.get_queryset()

        #Genres
        if genres:
            movies = movies.filter(
                moviegenres__genre_id__in=list(genres)
            ).distinct()

        #Min Year
        if min_year:
            movies = movies.filter(release_date__year__gte=int(min_year))

        #Max Year
        if max_year:
            movies = movies.filter(release_date__year__lte=int(max_year))

        if adult == "1":
            movies = movies.filter(adult=int(adult))
        
        if query_id:
            movies = movies.exclude(id=int(query_id))
    
        id_list = list(movies.values_list('id', flat=True))

        if len(id_list) < 2:
            return Response({
                'error': 'No movies match the criteria',
                'message': 'No movies found with the specified filters',
                'total': 0
            }, status=status.HTTP_404_NOT_FOUND)

        #Get Vectors from Movies
        all_vectors_query = Vectorized_Movies.objects.filter(id__in=id_list).values_list('movie_vector', flat=True)

        #Get Closest Vectors
        ids_movies = get_distance_vectors(43, all_vectors_query, query_vector, 5)
        if hasattr(ids_movies, 'flatten'):
            ids_movies = (ids_movies + 1).flatten()
        else:
            ids_movies = [id + 1 for id in ids_movies]

        #Pick Randoms ids
        ids_selected = np.random.choice(ids_movies.tolist(), size=2, replace=False).tolist()
        selected_movies = Movies.objects.filter(id__in=list(ids_selected))

        #Response
        serializer = self.get_serializer(selected_movies, many=True)
        response = serializer.data
        return Response(response, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def details(self, request):

        body_data = request.data
        ids_movie = body_data['ids']

        movies = Movies.objects.filter(id__in=list(ids_movie))

        serializer = self.get_serializer(movies, many=True)
        response = serializer.data

        return Response(response, status=status.HTTP_200_OK)