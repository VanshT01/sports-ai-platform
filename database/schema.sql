CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    league VARCHAR(100),
    country VARCHAR(100)
);

CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    home_team_id INT REFERENCES teams(id),
    away_team_id INT REFERENCES teams(id),
    home_score INT DEFAULT 0,
    away_score INT DEFAULT 0,
    status VARCHAR(50),
    match_date TIMESTAMP
);

CREATE TABLE match_events (
    id SERIAL PRIMARY KEY,
    match_id INT REFERENCES matches(id),
    team_id INT REFERENCES teams(id),
    event_type VARCHAR(50),
    minute INT,
    player_name VARCHAR(100),
    x FLOAT,
    y FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);