#-----------------------------------------------------------------
# CREATE MOVIE SECTION
#-----------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Movies (
  id INT AUTO_INCREMENT PRIMARY KEY,
  id_tmdb INT NOT NULL UNIQUE,
  adult BOOLEAN,
  backdrop_path VARCHAR(255),
  original_language VARCHAR(50),
  overview TEXT,
  keywords TEXT,
  popularity DECIMAL(10, 3),
  poster_path VARCHAR(255),
  release_date DATE,
  title VARCHAR(255),
  director VARCHAR(255),
  actors TEXT,
  vote_average DECIMAL(10, 3),
  vote_count INT,
  image_path VARCHAR(255),
  trailer_path VARCHAR(255),
  all_actors TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Vectorized_Movies (
  id INT PRIMARY KEY,
  id_tmdb INT NOT NULL UNIQUE,
  adult JSON,
  original_language JSON,
  title JSON,
  keywords JSON,
  popularity JSON,
  release_date JSON,
  director JSON,
  actors JSON,
  vote_average JSON,
  vote_count JSON,
  genres JSON,
  movie_vector JSON,

  FOREIGN KEY (id) 
    REFERENCES Movies(id) 
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS GenreMov (
  id INT AUTO_INCREMENT PRIMARY KEY,
  id_genre_tmdb INT NOT NULL UNIQUE,
  name VARCHAR(150) NOT NULL
);

CREATE TABLE IF NOT EXISTS Movie_Genres (
  id INT AUTO_INCREMENT PRIMARY KEY,
  movie_id INT NOT NULL,
  genre_id INT NOT NULL,

  FOREIGN KEY (movie_id) 
    REFERENCES Movies(id) 
    ON DELETE CASCADE,

  FOREIGN KEY (genre_id) 
    REFERENCES GenreMov(id) 
    ON DELETE CASCADE,

  UNIQUE KEY unique_movie_genre (movie_id, genre_id),

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Languages (
  code VARCHAR(2) PRIMARY KEY,
  english_name VARCHAR(100) NOT NULL,
  native_name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS Actors (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE,
  movie_count INT DEFAULT 0,
  total_votes BIGINT DEFAULT 0,
  avg_rating DECIMAL(5,3) DEFAULT 0,
  popularity_score DECIMAL(10,3) DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Movie_Actors (
  movie_id INT NOT NULL,
  actor_id INT NOT NULL,

  PRIMARY KEY (movie_id, actor_id),

  FOREIGN KEY (movie_id)
    REFERENCES Movies(id)
    ON DELETE CASCADE,

  FOREIGN KEY (actor_id)
    REFERENCES Actors(id)
    ON DELETE CASCADE
);

CREATE INDEX idx_movie_actors_actor ON Movie_Actors(actor_id);
CREATE INDEX idx_actors_popularity ON Actors(popularity_score DESC);

CREATE TABLE IF NOT EXISTS Directors (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE,
  movie_count INT DEFAULT 0,
  total_votes BIGINT DEFAULT 0,
  avg_rating DECIMAL(5,3) DEFAULT 0,
  popularity_score DECIMAL(10,3) DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Movie_Directors (
  movie_id INT NOT NULL,
  director_id INT NOT NULL,

  PRIMARY KEY (movie_id, director_id),

  FOREIGN KEY (movie_id)
    REFERENCES Movies(id)
    ON DELETE CASCADE,

  FOREIGN KEY (director_id)
    REFERENCES Directors(id)
    ON DELETE CASCADE
);

CREATE INDEX idx_movie_directors_director ON Movie_Directors(director_id);
CREATE INDEX idx_directors_popularity ON Directors(popularity_score DESC);

#-----------------------------------------------------------------
# CREATE PROVIDERS SECTION
#-----------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Providers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  tmdb_provider_id INT UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  logo_path VARCHAR(255),
  website_url VARCHAR(355),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Countries (
  code VARCHAR(2) PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Provider_Countries (
  provider_id INT NOT NULL,
  country_code VARCHAR(2) NOT NULL,
  media_type ENUM('movie', 'tv') NOT NULL,
  display_priority INT,

  PRIMARY KEY (provider_id, country_code, media_type),

  FOREIGN KEY (provider_id) 
    REFERENCES Providers(id) 
    ON DELETE CASCADE,

  FOREIGN KEY (country_code) 
    REFERENCES Countries(code) 
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Movie_Providers (
  movie_id INT NOT NULL,
  provider_id INT NOT NULL,
  country_code VARCHAR(2) NOT NULL,
  provider_type ENUM('flatrate', 'rent', 'buy', 'free', 'ads') NOT NULL,
  link VARCHAR(500),

  PRIMARY KEY (movie_id, provider_id, country_code, provider_type),

  FOREIGN KEY (movie_id) 
    REFERENCES Movies(id) 
    ON DELETE CASCADE,

  FOREIGN KEY (provider_id) 
    REFERENCES Providers(id) 
    ON DELETE CASCADE,

  FOREIGN KEY (country_code) 
    REFERENCES Countries(code) 
    ON DELETE CASCADE
);

CREATE INDEX idx_movie_providers_movie_country
ON Movie_Providers(movie_id, country_code);

CREATE INDEX idx_movie_providers_country
ON Movie_Providers(country_code);

CREATE INDEX idx_provider_countries_country_media
ON Provider_Countries(country_code, media_type);

CREATE INDEX idx_providers_tmdb_provider_id
ON Providers(tmdb_provider_id);

#-----------------------------------------------------------------
#CREATE TV SECTION
#-----------------------------------------------------------------

CREATE TABLE IF NOT EXISTS TV (
  id INT AUTO_INCREMENT PRIMARY KEY,
  id_tmdb INT NOT NULL UNIQUE,
  first_air_date DATE,
  name VARCHAR(255),
  origin_country VARCHAR(255),
  original_lenguaje VARCHAR(50),
  origin_name VARCHAR(80),
  overview TEXT,
  popularity DECIMAL(10, 3),
  poster_path VARCHAR(150),
  vote_average DECIMAL(10, 3),
  vote_count INT, 
  image_path VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS GenreTv (
	id INT AUTO_INCREMENT PRIMARY KEY,
  	id_genre_tmdb INT NOT NULL,
  	name VARCHAR(150)
 );

CREATE TABLE IF NOT EXISTS TV_Genres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tv_id INT NOT NULL,
    genre_id INT NOT NULL,
    
    FOREIGN KEY (tv_id) 
        REFERENCES TV(id) 
        ON DELETE CASCADE,
    
    FOREIGN KEY (genre_id) 
        REFERENCES GenreTv(id) 
        ON DELETE CASCADE,
    
    UNIQUE KEY unique_movie_genre (tv_id, genre_id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ProvidersTv (
	id INT AUTO_INCREMENT PRIMARY KEY,
  	id_provider_tmdb INT NOT NULL,
  	name VARCHAR(150)
 );

CREATE TABLE IF NOT EXISTS TV_Providers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tv_id INT NOT NULL,
    provider_id INT NOT NULL,
    
    FOREIGN KEY (tv_id) 
        REFERENCES TV(id) 
        ON DELETE CASCADE,
    
    FOREIGN KEY (provider_id) 
        REFERENCES ProvidersTv(id) 
        ON DELETE CASCADE,
    
    UNIQUE KEY unique_movie_genre (tv_id, provider_id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);