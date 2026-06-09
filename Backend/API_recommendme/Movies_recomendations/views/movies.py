from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from ..models import Movies, Vectorized_Movies
from ..serializers.movies import MovieSerializer, TwoOptionsRequestSerializer, DetailsRequestSerializer, startMoviesRequestSerializer
from ..utils import get_distance_vectors
import numpy as np
import random
import json


class MoviesViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Movies.objects.all()
    serializer_class = MovieSerializer

    @action(detail=False, methods=['get'])
    def start_movies(self, request):
        
        #Get Parameters
        genres_raw = request.GET.get("genres", None)
        if genres_raw is not None:
            try:
                genres = json.loads(genres_raw)
            except json.JSONDecodeError:
                return Response({
                    "genres": 'genres must be a valid INT JSON list, for example [1,2,3].'
                }, status=status.HTTP_404_NOT_FOUND)

        else:
            genres = None
            
        min_year = request.GET.get('min_year')
        max_year = request.GET.get('max_year')
        adult = request.GET.get('adult')

        data = {
            "genres": genres,
            "min_year": min_year,
            "max_year": max_year,
            "adult": adult,
        }

        serializer = startMoviesRequestSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        #Filter Parameters
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

        if adult == 1:
            movies = movies.filter(adult=int(adult))

        movies_list = list(movies)
        if len(movies_list) < 2:
            return Response({
                'error': 'No movies match the criteria',
                'message': 'No movies found with the specified filters',
                'total': len(movies_list)
            }, status=status.HTTP_404_NOT_FOUND)

        random_movies = random.sample(movies_list, 2)

        serializer_movies = self.get_serializer(random_movies, many=True)
        response = serializer_movies.data
        return Response(response, status=status.HTTP_200_OK)




    @action(detail=False, methods=['post'])
    def two_options(self, request):
        serializer = TwoOptionsRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        #Get vector from request
        body_data = request.data
        query_vector = body_data['vector']

        #Filter Movies by variables
        genres = body_data['genres']
        min_year = body_data['min_year']
        max_year = body_data['max_year']
        adult = body_data['adult']
        query_id = body_data['ids']

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

        if adult == 1:
            movies = movies.filter(adult=int(adult))
        
        if query_id:
            movies = movies.exclude(id__in=list(query_id))
    
        id_list = list(movies.values_list('id', flat=True))

        if len(id_list) < 2:
            return Response({
                'error': 'No movies match the criteria',
                'message': 'No movies found with the specified filters',
                'total': 0
            }, status=status.HTTP_404_NOT_FOUND)

        #Get Vectors from Movies (preserving ID order aligned with FAISS index)
        vectorized_qs = Vectorized_Movies.objects.filter(id__in=id_list).values_list('id', 'movie_vector')
        actual_ids = [row[0] for row in vectorized_qs]
        vectors = [row[1] for row in vectorized_qs]

        #Get Closest Vectors (returns positional indices into `vectors` array)
        faiss_indices = get_distance_vectors(43, vectors, query_vector, 5).flatten()

        #Map FAISS positional indices back to real movie IDs
        ids_movies = [actual_ids[i] for i in faiss_indices if i < len(actual_ids)]

        #Pick Randoms ids
        ids_selected = np.random.choice(ids_movies, size=2, replace=False).tolist()
        selected_movies = Movies.objects.filter(id__in=list(ids_selected))

        #Response
        serializer_movies = self.get_serializer(selected_movies, many=True)
        response = serializer_movies.data
        return Response(response, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def details(self, request):
        serializer = DetailsRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        body_data = request.data
        ids_movie = body_data['ids']

        movies = Movies.objects.filter(id__in=list(ids_movie))

        serializer = self.get_serializer(movies, many=True)
        response = serializer.data

        return Response(response, status=status.HTTP_200_OK)