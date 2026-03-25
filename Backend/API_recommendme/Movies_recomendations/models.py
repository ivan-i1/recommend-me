from django.db import models

# Create your models here.
class Genremov(models.Model):
    id_genre_tmdb = models.IntegerField()
    name = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'GenreMov'

class Genretv(models.Model):
    id_genre_tmdb = models.IntegerField()
    name = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'GenreTv'

class MovieGenres(models.Model):
    movie = models.ForeignKey('Movies', models.DO_NOTHING)
    genre = models.ForeignKey(Genremov, models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Movie_Genres'
        unique_together = (('movie', 'genre'),)

class MovieProviders(models.Model):
    movie = models.ForeignKey('Movies', models.DO_NOTHING)
    provider = models.ForeignKey('Providersmov', models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Movie_Providers'
        unique_together = (('movie', 'provider'),)

class Movies(models.Model):
    id_tmdb = models.IntegerField(unique=True)
    adult = models.IntegerField(blank=True, null=True)
    backdrop_path = models.CharField(max_length=150, blank=True, null=True)
    original_lenguaje = models.CharField(max_length=50, blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    keywords = models.JSONField()
    popularity = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    poster_path = models.CharField(max_length=150, blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    director = models.CharField(max_length=255, blank=True, null=True)
    actors = models.JSONField()
    vote_average = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    vote_count = models.IntegerField(blank=True, null=True)
    image_path = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Movies'

class Providersmov(models.Model):
    id_provider_tmdb = models.IntegerField()
    name = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ProvidersMov'

class Providerstv(models.Model):
    id_provider_tmdb = models.IntegerField()
    name = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ProvidersTv'


class Tv(models.Model):
    id_tmdb = models.IntegerField(unique=True)
    first_air_date = models.DateField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    origin_country = models.CharField(max_length=255, blank=True, null=True)
    original_lenguaje = models.CharField(max_length=50, blank=True, null=True)
    origin_name = models.CharField(max_length=80, blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    popularity = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    poster_path = models.CharField(max_length=150, blank=True, null=True)
    vote_average = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    vote_count = models.IntegerField(blank=True, null=True)
    image_path = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TV'

class TvGenres(models.Model):
    tv = models.ForeignKey(Tv, models.DO_NOTHING)
    genre = models.ForeignKey(Genretv, models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TV_Genres'
        unique_together = (('tv', 'genre'),)

class TvProviders(models.Model):
    tv = models.ForeignKey(Tv, models.DO_NOTHING)
    provider = models.ForeignKey(Providerstv, models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TV_Providers'
        unique_together = (('tv', 'provider'),)

class Vectorized_Movies(models.Model):
    id = models.IntegerField(primary_key=True)
    id_tmdb = models.IntegerField(unique=True)
    adult = models.JSONField()
    original_lenguaje = models.JSONField() 
    title = models.JSONField()
    keywords = models.JSONField()
    popularity = models.JSONField()
    release_date = models.JSONField()
    director = models.JSONField()
    actors = models.JSONField()
    vote_average = models.JSONField()
    vote_count = models.JSONField()
    gender = models.JSONField()  
    movie_vector = models.JSONField()

    class Meta:
        managed = False
        db_table = 'Vectorized_Movies'