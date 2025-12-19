CREATE DATABASE IF NOT EXISTS imdb_movies;
USE imdb_movies;

CREATE TABLE IF NOT EXISTS top_movies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rank_num INT,
    title VARCHAR(255),
    year VARCHAR(10),
    duration VARCHAR(20),
    rating VARCHAR(10),
    poster_url TEXT,
    detail_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);