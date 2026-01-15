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

import hashlib
import hmac
import logging
import os

import git
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from auth import authenticate, login_manager, register_user
from db import db_read, db_write

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

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
    hash_algorithm, github_signature = x_hub_signature.split("=", 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, "latin-1")
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)


# DON'T CHANGE
@app.post("/update_server")
def webhook():
    x_hub_signature = request.headers.get("X-Hub-Signature")
    if is_valid_signature(x_hub_signature, request.data, W_SECRET):
        repo = git.Repo("./mysite")
        origin = repo.remotes.origin
        origin.pull()
        return "Updated PythonAnywhere successfully", 200
    return "Unathorized", 401


# ---------------------------
# Auth routes
# ---------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        user = authenticate(request.form["username"], request.form["password"])

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
        footer_link_label="Registrieren",
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
        footer_link_label="Einloggen",
    )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


# ---------------------------
# App routes (Turnier)
# ---------------------------
@app.route("/", methods=["GET"])
@login_required
def index():
    # kleine Startseite / Dashboard
    # Optional: letzte 5 Spiele anzeigen
    spiele = db_read(
        """
        SELECT
            s.spiel_id,
            ht.name AS heimteam,
            at.name AS auswaertsteam,
            s.tore_heimteam,
            s.tore_auswaertsteam
        FROM spiel s
        JOIN team ht ON s.heimteam_id = ht.team_id
        JOIN team at ON s.auswaertsteam_id = at.team_id
        ORDER BY s.spiel_id DESC
        LIMIT 5;
        """
    ) or []
    return render_template("willkommen.html", letzte_spiele=spiele)


@app.route("/teams", methods=["GET"])
@login_required
def teams():
    rows = db_read("SELECT team_id, name, trainer FROM team ORDER BY name;") or []
    return render_template("teams.html", teams=rows)


@app.route("/spielplan", methods=["GET"])
@login_required
def spielplan():
    # liest Begegnungen aus dem Spielplan
    rows = db_read(
        """
        SELECT
            sp.spielplan_id,
            b.begegnung_id,
            ht.name AS heimteam,
            at.name AS auswaertsteam
        FROM spielplan sp
        JOIN begegnung b ON sp.begegnung_id = b.begegnung_id
        JOIN team ht ON b.heimteam_id = ht.team_id
        JOIN team at ON b.auswaertsteam_id = at.team_id
        ORDER BY sp.spielplan_id DESC;
        """
    ) or []
    return render_template("spielplan.html", plan=rows)


@app.route("/spiele", methods=["GET"])
@login_required
def spiele():
    # alle Spiele + Ergebnis
    rows = db_read(
        """
        SELECT
            s.spiel_id,
            ht.name AS heimteam,
            at.name AS auswaertsteam,
            s.tore_heimteam,
            s.tore_auswaertsteam
        FROM spiel s
        JOIN team ht ON s.heimteam_id = ht.team_id
        JOIN team at ON s.auswaertsteam_id = at.team_id
        ORDER BY s.spiel_id DESC;
        """
    ) or []
    return render_template("spiele.html", spiele=rows)


@app.route("/spiel/eintragen", methods=["GET", "POST"])
@login_required
def spiel_eintragen():
    # Formular: neues Spiel/Ergebnis eintragen
    teams = db_read("SELECT team_id, name FROM team ORDER BY name;") or []

    if request.method == "GET":
        return render_template("spiel_eintragen.html", teams=teams, error=None)

    heimteam_id = int(request.form["heimteam_id"])
    auswaertsteam_id = int(request.form["auswaertsteam_id"])
    tore_heim = int(request.form.get("tore_heimteam", 0))
    tore_aus = int(request.form.get("tore_auswaertsteam", 0))

    if heimteam_id == auswaertsteam_id:
        return render_template(
            "spiel_eintragen.html",
            teams=teams,
            error="Heimteam und Auswärtsteam dürfen nicht gleich sein.",
        )

    db_write(
        """
        INSERT INTO spiel (heimteam_id, auswaertsteam_id, tore_heimteam, tore_auswaertsteam)
        VALUES (%s, %s, %s, %s);
        """,
        (heimteam_id, auswaertsteam_id, tore_heim, tore_aus),
    )

    return redirect(url_for("spiele"))


@app.route("/tabelle", methods=["GET"])
@login_required
def tabelle_view():
    # Variante A: Wenn ihr tabelle.siege manuell pflegt
    # rows = db_read("""
    #     SELECT t.name AS team, tab.gruppe_id, tab.siege
    #     FROM tabelle tab
    #     JOIN team t ON tab.team_id = t.team_id
    #     ORDER BY tab.siege DESC, t.name;
    # """) or []

    # Variante B (empfohlen): Siege aus spiel berechnen (keine Redundanz)
    rows = db_read(
        """
        SELECT
            t.team_id,
            t.name,
            SUM(
                CASE
                    WHEN s.heimteam_id = t.team_id AND s.tore_heimteam > s.tore_auswaertsteam THEN 1
                    WHEN s.auswaertsteam_id = t.team_id AND s.tore_auswaertsteam > s.tore_heimteam THEN 1
                    ELSE 0
                END
            ) AS siege
        FROM team t
        LEFT JOIN spiel s
            ON t.team_id IN (s.heimteam_id, s.auswaertsteam_id)
        GROUP BY t.team_id, t.name
        ORDER BY siege DESC, t.name;
        """
    ) or []

    return render_template("tabelle.html", tabelle=rows)


# ---------------------------
# "Mein Turnier" Feature (wie Backstube, nur Turnier-Favoriten)
# ---------------------------
# Dafür braucht ihr eine Tabelle, z.B.:
# CREATE TABLE favorit_spiele (
#   user_id INT NOT NULL,
#   spiel_id INT NOT NULL,
#   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#   PRIMARY KEY(user_id, spiel_id)
# );

@app.route("/meine_spiele", methods=["GET"])
@login_required
def meine_spiele():
    rows = db_read(
        """
        SELECT
            s.spiel_id,
            ht.name AS heimteam,
            at.name AS auswaertsteam,
            s.tore_heimteam,
            s.tore_auswaertsteam
        FROM favorit_spiele f
        JOIN spiel s ON s.spiel_id = f.spiel_id
        JOIN team ht ON s.heimteam_id = ht.team_id
        JOIN team at ON s.auswaertsteam_id = at.team_id
        WHERE f.user_id = %s
        ORDER BY f.created_at DESC;
        """,
        (current_user.id,),
    ) or []
    return render_template("meine_spiele.html", spiele=rows)


@app.post("/meine_spiele/toggle")
@login_required
def meine_spiele_toggle():
    spiel_id = int(request.form["spiel_id"])

    existing = db_read(
        "SELECT 1 FROM favorit_spiele WHERE user_id=%s AND spiel_id=%s",
        (current_user.id, spiel_id),
    )

    if existing:
        db_write(
            "DELETE FROM favorit_spiele WHERE user_id=%s AND spiel_id=%s",
            (current_user.id, spiel_id),
        )
        return {"saved": False}

    db_write(
        "INSERT INTO favorit_spiele (user_id, spiel_id) VALUES (%s, %s)",
        (current_user.id, spiel_id),
    )
    return {"saved": True}





if __name__ == "__main__":
    app.run()
