from rest_framework.routers import DefaultRouter
from .views.movies import MoviesViewSet
from .views.general_details import DetailMovieViewSet

router = DefaultRouter()
router.register(r'movies', MoviesViewSet, basename='movies')
router.register(r'details', DetailMovieViewSet, basename='details')

urlpatterns = router.urls