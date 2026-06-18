from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from ..models import Movies, Vectorized_Movies, MovieActors, MovieDirectors
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

        original_language_raw = request.GET.get("original_language", None)
        if original_language_raw is not None:
            try:
                original_language = json.loads(original_language_raw)
            except json.JSONDecodeError:
                return Response({
                    "original_language": 'original_language must be a valid string JSON list, for example ["en","es"].'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            original_language = []

        providers_raw = request.GET.get("providers", None)
        if providers_raw is not None:
            try:
                providers = json.loads(providers_raw)
            except json.JSONDecodeError:
                return Response({
                    "providers": 'providers must be a valid INT JSON list, for example [1,2,3].'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            providers = []

        actors_raw = request.GET.get("actors", None)
        if actors_raw is not None:
            try:
                actors = json.loads(actors_raw)
            except json.JSONDecodeError:
                return Response({
                    "actors": 'actors must be a valid INT JSON list, for example [1,2,3].'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            actors = []

        directors_raw = request.GET.get("directors", None)
        if directors_raw is not None:
            try:
                directors = json.loads(directors_raw)
            except json.JSONDecodeError:
                return Response({
                    "directors": 'directors must be a valid INT JSON list, for example [1,2,3].'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            directors = []

        data = {
            "genres": genres,
            "min_year": min_year,
            "max_year": max_year,
            "adult": adult,
            "original_language": original_language,
            "providers": providers,
            "actors": actors,
            "directors": directors,
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

        #Original Language
        if original_language:
            movies = movies.filter(original_language__in=list(original_language))

        #Providers
        if providers:
            movies = movies.filter(
                movieproviders__provider_id__in=list(providers)
            ).distinct()

        #Actors
        if actors:
            actor_movie_ids = MovieActors.objects.filter(
                actor_id__in=list(actors)
            ).values_list('movie_id', flat=True).distinct()
            movies = movies.filter(id__in=actor_movie_ids)

        #Directors
        if directors:
            director_movie_ids = MovieDirectors.objects.filter(
                director_id__in=list(directors)
            ).values_list('movie_id', flat=True).distinct()
            movies = movies.filter(id__in=director_movie_ids)

        movies_list = list(movies)
        if len(movies_list) < 2:
            return Response({
                'error': 'No movies match the criteria',
                'message': 'No movies found with the specified filters',
                'total': len(movies_list)
            }, status=status.HTTP_404_NOT_FOUND)

        random_movies = random.sample(movies_list, min(12, len(movies_list)))

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
        original_language = body_data['original_language']
        providers = body_data['providers']
        actors = body_data['actors']
        directors = body_data['directors']

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

        #Original Language
        if original_language:
            movies = movies.filter(original_language__in=list(original_language))

        #Providers
        if providers:
            movies = movies.filter(
                movieproviders__provider_id__in=list(providers)
            ).distinct()

        #Actors
        if actors:
            actor_movie_ids = MovieActors.objects.filter(
                actor_id__in=list(actors)
            ).values_list('movie_id', flat=True).distinct()
            movies = movies.filter(id__in=actor_movie_ids)

        #Directors
        if directors:
            director_movie_ids = MovieDirectors.objects.filter(
                director_id__in=list(directors)
            ).values_list('movie_id', flat=True).distinct()
            movies = movies.filter(id__in=director_movie_ids)

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

        #Map FAISS positional indices back to real movie IDs (deduplicated)
        seen = set()
        ids_movies = []
        for i in faiss_indices:
            if i < len(actual_ids) and actual_ids[i] not in seen:
                seen.add(actual_ids[i])
                ids_movies.append(actual_ids[i])

        if len(ids_movies) < 2:
            return Response({
                'error': 'No movies match the criteria',
                'message': 'No movies found with the specified filters',
                'total': len(ids_movies)
            }, status=status.HTTP_404_NOT_FOUND)

        #Pick Randoms ids
        ids_selected = np.random.choice(ids_movies, size=2, replace=False).tolist()
        selected_movies = list(Movies.objects.filter(id__in=list(ids_selected)))
        random.shuffle(selected_movies)

        #Response
        serializer_movies = self.get_serializer(selected_movies, many=True)
        response = serializer_movies.data
        return Response(response, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def twelve_options(self, request):
        serializer = TwoOptionsRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        body_data = request.data
        query_vector = body_data['vector']

        genres = body_data['genres']
        min_year = body_data['min_year']
        max_year = body_data['max_year']
        adult = body_data['adult']
        query_id = body_data['ids']
        original_language = body_data['original_language']
        providers = body_data['providers']
        actors = body_data['actors']
        directors = body_data['directors']

        movies = self.get_queryset()

        if genres:
            movies = movies.filter(
                moviegenres__genre_id__in=list(genres)
            ).distinct()

        if min_year:
            movies = movies.filter(release_date__year__gte=int(min_year))

        if max_year:
            movies = movies.filter(release_date__year__lte=int(max_year))

        if adult == 1:
            movies = movies.filter(adult=int(adult))

        if original_language:
            movies = movies.filter(original_language__in=list(original_language))

        if providers:
            movies = movies.filter(
                movieproviders__provider_id__in=list(providers)
            ).distinct()

        if actors:
            actor_movie_ids = MovieActors.objects.filter(
                actor_id__in=list(actors)
            ).values_list('movie_id', flat=True).distinct()
            movies = movies.filter(id__in=actor_movie_ids)

        if directors:
            director_movie_ids = MovieDirectors.objects.filter(
                director_id__in=list(directors)
            ).values_list('movie_id', flat=True).distinct()
            movies = movies.filter(id__in=director_movie_ids)

        if query_id:
            movies = movies.exclude(id__in=list(query_id))

        id_list = list(movies.values_list('id', flat=True))

        if len(id_list) < 2:
            return Response({
                'error': 'No movies match the criteria',
                'message': 'No movies found with the specified filters',
                'total': len(id_list)
            }, status=status.HTTP_404_NOT_FOUND)

        vectorized_qs = Vectorized_Movies.objects.filter(id__in=id_list).values_list('id', 'movie_vector')
        actual_ids = [row[0] for row in vectorized_qs]
        vectors = [row[1] for row in vectorized_qs]

        faiss_indices = get_distance_vectors(43, vectors, query_vector, 20).flatten()

        seen = set()
        ids_movies = []
        for i in faiss_indices:
            if i < len(actual_ids) and actual_ids[i] not in seen:
                seen.add(actual_ids[i])
                ids_movies.append(actual_ids[i])

        if len(ids_movies) < 2:
            return Response({
                'error': 'No movies match the criteria',
                'message': 'No movies found with the specified filters',
                'total': len(ids_movies)
            }, status=status.HTTP_404_NOT_FOUND)

        ids_selected = np.random.choice(ids_movies, size=min(12, len(ids_movies)), replace=False).tolist()
        selected_movies = list(Movies.objects.filter(id__in=list(ids_selected)))
        random.shuffle(selected_movies)

        serializer_movies = self.get_serializer(selected_movies, many=True)
        return Response(serializer_movies.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='searchMovie')
    def search_movie(self, request):
        q = request.query_params.get('q', '').strip()
        if not q:
            return Response(
                {'error': 'Query parameter "q" is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        movies = Movies.objects.filter(title__icontains=q).order_by('-popularity')[:20]
        serializer = self.get_serializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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