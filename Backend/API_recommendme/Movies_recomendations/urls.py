from rest_framework.routers import DefaultRouter
from .views.movies import MoviesViewSet
from .views.general_details import GenreMovieViewSet

router = DefaultRouter()
router.register(r'movies', MoviesViewSet, basename='movies')
router.register(r'details', GenreMovieViewSet, basename='details')

urlpatterns = router.urls