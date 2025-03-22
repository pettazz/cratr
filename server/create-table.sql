CREATE TABLE IF NOT EXISTS Meteorites (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    class VARCHAR(5),
    mass FLOAT,
    year INT,
    lat FLOAT,
    lon FLOAT
);