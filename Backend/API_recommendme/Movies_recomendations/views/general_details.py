from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from ..models import Genremov
from ..serializers.general_details import GenreMovieSerializer, GenreRequestSerializer


class GenreMovieViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Genremov.objects.all()
    serializer_class = GenreMovieSerializer

    @action(detail=False, methods=['get'])
    def genres(self, request):

        request_serializer = GenreRequestSerializer(
            data=request.query_params,
            context={"request": request}
        )
        request_serializer.is_valid(raise_exception=True)

        
        serializer = self.get_serializer(self.queryset, many=True)
        response = serializer.data
        return Response(response, status=status.HTTP_200_OK)

