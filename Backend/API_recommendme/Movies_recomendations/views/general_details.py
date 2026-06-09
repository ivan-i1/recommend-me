from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from ..models import Genremov, Providers, Countries
from ..serializers.general_details import GenreMovieSerializer, ValidRequestSerializer, ProvidersSerializer, CountriesSerializer


class DetailMovieViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):

    @action(detail=False, methods=['get'])
    def genres(self, request):
        request_serializer = ValidRequestSerializer(
            data=request.query_params,
            context={"request": request}
        )
        request_serializer.is_valid(raise_exception=True)

        serializer = GenreMovieSerializer(Genremov.objects.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def providers(self, request):
        request_serializer = ValidRequestSerializer(
            data=request.query_params,
            context={"request": request}
        )
        request_serializer.is_valid(raise_exception=True)

        serializer = ProvidersSerializer(Providers.objects.all(), many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def countries(self, request):
        request_serializer = ValidRequestSerializer(
            data=request.query_params,
            context={"request": request}
        )
        request_serializer.is_valid(raise_exception=True)

        serializer = CountriesSerializer(Countries.objects.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
