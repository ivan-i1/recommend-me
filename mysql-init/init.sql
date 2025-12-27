#-----------------------------------------------------------------
#CREATE MOVIE SECTION
#-----------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Movies (
  id INT AUTO_INCREMENT PRIMARY KEY,
  id_tmdb INT NOT NULL UNIQUE,
  adult BOOLEAN,
  backdrop_path VARCHAR(150),
  original_lenguaje VARCHAR(50),
  overview TEXT,
  popularity DECIMAL(10, 3),
  poster_path VARCHAR(150),
  release_date DATE,
  title VARCHAR(255),
  vote_average DECIMAL(10, 3),
  vote_count INT,
  image_path VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS GenreMov (
	id INT AUTO_INCREMENT PRIMARY KEY,
  	id_genre_tmdb INT NOT NULL,
  	name VARCHAR(150)
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

CREATE TABLE IF NOT EXISTS ProvidersMov (
	id INT AUTO_INCREMENT PRIMARY KEY,
  	id_provider_tmdb INT NOT NULL,
  	name VARCHAR(150)
 );

CREATE TABLE IF NOT EXISTS Movie_Providers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT NOT NULL,
    provider_id INT NOT NULL,
    
    FOREIGN KEY (movie_id) 
        REFERENCES Movies(id) 
        ON DELETE CASCADE,
    
    FOREIGN KEY (provider_id) 
        REFERENCES ProvidersMov(id) 
        ON DELETE CASCADE,
    
    UNIQUE KEY unique_movie_genre (movie_id, provider_id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


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