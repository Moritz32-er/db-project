CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(250) NOT NULL UNIQUE,
    password VARCHAR(250) NOT NULL
);

CREATE TABLE todos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL, 
    content VARCHAR(100),
    due DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE team (
    team_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    trainer VARCHAR(100)
);

CREATE TABLE mitarbeiter (
    mitarbeiter_id INT AUTO_INCREMENT PRIMARY KEY
);

CREATE TABLE team_mitarbeiter (
    team_id INT,
    mitarbeiter_id INT,
    PRIMARY KEY (team_id, mitarbeiter_id),
    FOREIGN KEY (team_id) REFERENCES team(team_id),
    FOREIGN KEY (mitarbeiter_id) REFERENCES mitarbeiter(mitarbeiter_id)
);

CREATE TABLE spiel (
    spiel_id INT AUTO_INCREMENT PRIMARY KEY,
    heimteam_id INT NOT NULL,
    auswaertsteam_id INT NOT NULL,
    tore_heimteam INT DEFAULT 0,
    tore_auswaertsteam INT DEFAULT 0,
    FOREIGN KEY (heimteam_id) REFERENCES team(team_id),
    FOREIGN KEY (auswaertsteam_id) REFERENCES team(team_id)
);

CREATE TABLE begegnung (
    begegnung_id INT AUTO_INCREMENT PRIMARY KEY,
    heimteam_id INT NOT NULL,
    auswaertsteam_id INT NOT NULL,
    FOREIGN KEY (heimteam_id) REFERENCES team(team_id),
    FOREIGN KEY (auswaertsteam_id) REFERENCES team(team_id)
);

CREATE TABLE spielplan (
    spielplan_id INT AUTO_INCREMENT PRIMARY KEY,
    begegnung_id INT NOT NULL,
    FOREIGN KEY (begegnung_id) REFERENCES begegnung(begegnung_id)
);

CREATE TABLE tabelle (
    tabellen_id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INT UNIQUE NOT NULL,
    gruppe_id INT,
    siege INT DEFAULT 0,
    FOREIGN KEY (team_id) REFERENCES team(team_id)
);






INSERT INTO users (username, password) VALUES
('admin', 'admin123'),
('spieler1', 'passwort');



INSERT INTO todos (user_id, content, due) VALUES
(1, 'Spielplan erstellen', '2026-01-20 18:00:00'),
(1, 'Teams erfassen', '2026-01-18 12:00:00'),
(2, 'Erstes Spiel eintragen', '2026-01-22 20:00:00');



INSERT INTO team (name, trainer) VALUES
('FC Alpha', 'Trainer A'),
('FC Beta', 'Trainer B'),
('FC Gamma', 'Trainer C');


INSERT INTO mitarbeiter () VALUES
(),
(),
();



INSERT INTO team_mitarbeiter (team_id, mitarbeiter_id) VALUES
(1, 1),
(1, 2),
(2, 3);



INSERT INTO begegnung (heimteam_id, auswaertsteam_id) VALUES
(1, 2),
(2, 3),
(3, 1);



INSERT INTO spielplan (begegnung_id) VALUES
(1),
(2),
(3);



INSERT INTO spiel (heimteam_id, auswaertsteam_id, tore_heimteam, tore_auswaertsteam) VALUES
(1, 2, 2, 1),
(2, 3, 0, 0),
(3, 1, 3, 2);



INSERT INTO tabelle (team_id, gruppe_id, siege) VALUES
(1, 1, 1),
(2, 1, 0),
(3, 1, 1);
