from flask import Flask, redirect, render_template, request, url_for
from dotenv import load_dotenv
import os
import git
import hmac
import hashlib
from db import db_read, db_write
from auth import login_manager, authenticate, register_user
from flask_login import login_user, logout_user, login_required, current_user
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Load .env variables
load_dotenv()
W_SECRET = os.getenv("W_SECRET")

# Init flask app
app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = "supersecret"

# Init auth
login_manager.init_app(app)
login_manager.login_view = "login"

# DON'T CHANGE
def is_valid_signature(x_hub_signature, data, private_key):
    hash_algorithm, github_signature = x_hub_signature.split('=', 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, 'latin-1')
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)

# DON'T CHANGE
@app.post('/update_server')
def webhook():
    x_hub_signature = request.headers.get('X-Hub-Signature')
    if is_valid_signature(x_hub_signature, request.data, W_SECRET):
        repo = git.Repo('./mysite')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    return 'Unathorized', 401

# Auth routes
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        user = authenticate(
            request.form["username"],
            request.form["password"]
        )

        if user:
            login_user(user)
            return redirect(url_for("index"))

        error = "Benutzername oder Passwort ist falsch."

    return render_template(
        "auth.html",
        title="In dein Konto einloggen",
        action=url_for("login"),
        button_label="Einloggen",
        error=error,
        footer_text="Noch kein Konto?",
        footer_link_url=url_for("register"),
        footer_link_label="Registrieren"
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        ok = register_user(username, password)
        if ok:
            return redirect(url_for("login"))

        error = "Benutzername existiert bereits."

    return render_template(
        "auth.html",
        title="Neues Konto erstellen",
        action=url_for("register"),
        button_label="Registrieren",
        error=error,
        footer_text="Du hast bereits ein Konto?",
        footer_link_url=url_for("login"),
        footer_link_label="Einloggen"
    )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))



# App routes
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # GET
    if request.method == "GET":
        todos = db_read("SELECT id, content, due FROM todos WHERE user_id=%s ORDER BY due", (current_user.id,))
        return render_template("main_page.html", todos=todos)

    # POST
    content = request.form["contents"]
    due = request.form["due_at"]
    db_write("INSERT INTO todos (user_id, content, due) VALUES (%s, %s, %s)", (current_user.id, content, due, ))
    return redirect(url_for("index"))

@app.post("/complete")
@login_required
def complete():
    todo_id = request.form.get("id")
    db_write("DELETE FROM todos WHERE user_id=%s AND id=%s", (current_user.id, todo_id,))
    return redirect(url_for("index"))

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
CREATE VIEW v_spiele_teams AS
SELECT
    s.spiel_id,
    ht.name AS heimteam,
    at.name AS auswaertsteam,
    s.tore_heimteam,
    s.tore_auswaertsteam
FROM spiel s
JOIN team ht ON s.heimteam_id = ht.team_id
JOIN team at ON s.auswaertsteam_id = at.team_id;

CREATE VIEW v_spielplan AS
SELECT
    sp.spielplan_id,
    b.begegnung_id,
    ht.name AS heimteam,
    at.name AS auswaertsteam
FROM spielplan sp
JOIN begegnung b ON sp.begegnung_id = b.begegnung_id
JOIN team ht ON b.heimteam_id = ht.team_id
JOIN team at ON b.auswaertsteam_id = at.team_id;

CREATE VIEW v_tabelle AS
SELECT
    t.name AS team,
    tab.gruppe_id,
    tab.siege
FROM tabelle tab
JOIN team t ON tab.team_id = t.team_id
ORDER BY tab.siege DESC;

CREATE VIEW v_siege_berechnet AS
SELECT
    t.team_id,
    t.name,
    SUM(
        CASE
            WHEN s.heimteam_id = t.team_id
                 AND s.tore_heimteam > s.tore_auswaertsteam THEN 1
            WHEN s.auswaertsteam_id = t.team_id
                 AND s.tore_auswaertsteam > s.tore_heimteam THEN 1
            ELSE 0
        END
    ) AS siege
FROM team t
LEFT JOIN spiel s
    ON t.team_id IN (s.heimteam_id, s.auswaertsteam_id)
GROUP BY t.team_id, t.name;

CREATE VIEW v_team_mitarbeiter AS
SELECT
    t.name AS team,
    m.mitarbeiter_id
FROM team_mitarbeiter tm
JOIN team t ON tm.team_id = t.team_id
JOIN mitarbeiter m ON tm.mitarbeiter_id = m.mitarbeiter_id;



if __name__ == "__main__":
    app.run()
