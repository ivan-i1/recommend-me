from django.db import models


# -----------------------------------------------
# GENRE SECTION
# -----------------------------------------------

class Genremov(models.Model):
    id_genre_tmdb = models.IntegerField(unique=True)
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


# -----------------------------------------------
# MOVIES SECTION
# -----------------------------------------------

class Movies(models.Model):
    id_tmdb = models.IntegerField(unique=True)
    adult = models.BooleanField(blank=True, null=True)
    backdrop_path = models.CharField(max_length=255, blank=True, null=True)
    original_language = models.CharField(max_length=50, blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    popularity = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    poster_path = models.CharField(max_length=255, blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    director = models.CharField(max_length=255, blank=True, null=True)
    actors = models.TextField(blank=True, null=True)
    vote_average = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    vote_count = models.IntegerField(blank=True, null=True)
    image_path = models.CharField(max_length=255, blank=True, null=True)
    trailer_path = models.CharField(max_length=255, blank=True, null=True)
    all_actors = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Movies'


class Vectorized_Movies(models.Model):
    id = models.IntegerField(primary_key=True)
    id_tmdb = models.IntegerField(unique=True)
    adult = models.JSONField(blank=True, null=True)
    original_language = models.JSONField(blank=True, null=True)
    title = models.JSONField(blank=True, null=True)
    keywords = models.JSONField(blank=True, null=True)
    popularity = models.JSONField(blank=True, null=True)
    release_date = models.JSONField(blank=True, null=True)
    director = models.JSONField(blank=True, null=True)
    actors = models.JSONField(blank=True, null=True)
    vote_average = models.JSONField(blank=True, null=True)
    vote_count = models.JSONField(blank=True, null=True)
    genres = models.JSONField(blank=True, null=True)
    movie_vector = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Vectorized_Movies'


class MovieGenres(models.Model):
    movie = models.ForeignKey(Movies, models.DO_NOTHING, db_column='movie_id')
    genre = models.ForeignKey(Genremov, models.DO_NOTHING, db_column='genre_id')
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Movie_Genres'
        unique_together = (('movie', 'genre'),)


# -----------------------------------------------
# PROVIDERS SECTION
# -----------------------------------------------

class Countries(models.Model):
    code = models.CharField(primary_key=True, max_length=2)
    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Countries'


class Providers(models.Model):
    tmdb_provider_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    logo_path = models.CharField(max_length=255, blank=True, null=True)
    website_url = models.CharField(max_length=355, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Providers'


class ProviderCountries(models.Model):
    provider = models.ForeignKey(Providers, models.DO_NOTHING, db_column='provider_id')
    country = models.ForeignKey(Countries, models.DO_NOTHING, db_column='country_code', to_field='code')
    media_type = models.CharField(max_length=5)
    display_priority = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Provider_Countries'
        unique_together = (('provider', 'country', 'media_type'),)


class MovieProviders(models.Model):
    movie = models.ForeignKey(Movies, models.DO_NOTHING, db_column='movie_id')
    provider = models.ForeignKey(Providers, models.DO_NOTHING, db_column='provider_id')
    country = models.ForeignKey(Countries, models.DO_NOTHING, db_column='country_code', to_field='code')
    provider_type = models.CharField(max_length=10)
    link = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Movie_Providers'
        unique_together = (('movie', 'provider', 'country', 'provider_type'),)


# -----------------------------------------------
# TV SECTION
# -----------------------------------------------

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


class Providerstv(models.Model):
    id_provider_tmdb = models.IntegerField()
    name = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ProvidersTv'


class TvGenres(models.Model):
    tv = models.ForeignKey(Tv, models.DO_NOTHING, db_column='tv_id')
    genre = models.ForeignKey(Genretv, models.DO_NOTHING, db_column='genre_id')
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TV_Genres'
        unique_together = (('tv', 'genre'),)


class TvProviders(models.Model):
    tv = models.ForeignKey(Tv, models.DO_NOTHING, db_column='tv_id')
    provider = models.ForeignKey(Providerstv, models.DO_NOTHING, db_column='provider_id')
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TV_Providers'
        unique_together = (('tv', 'provider'),)
