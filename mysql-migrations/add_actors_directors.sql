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

#-----------------------------------------------------------------

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
