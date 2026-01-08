from rest_framework.routers import DefaultRouter
from .views import MoviesViewSet

router = DefaultRouter()
router.register(r'movies', MoviesViewSet, basename='movies')

urlpatterns = router.urls