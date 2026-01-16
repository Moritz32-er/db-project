from flask import Flask, redirect, render_template, request, url_for
from dotenv import load_dotenv
import os
import git
import hmac
import hashlib
import logging

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
)

from auth import login_manager, authenticate, register_user
from db import db_read, db_write

# ---------------------------
# Setup
# ---------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

load_dotenv()
W_SECRET = os.getenv("W_SECRET")

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = "supersecret"

login_manager.init_app(app)
login_manager.login_view = "login"

# ---------------------------
# GitHub Webhook (NICHT ÄNDERN)
# ---------------------------
def is_valid_signature(x_hub_signature, data, private_key):
    hash_algorithm, github_signature = x_hub_signature.split("=", 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, "latin-1")
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)

@app.post("/update_server")
def webhook():
    x_hub_signature = request.headers.get("X-Hub-Signature")
    if is_valid_signature(x_hub_signature, request.data, W_SECRET):
        repo = git.Repo("./mysite")
        repo.remotes.origin.pull()
        return "Updated PythonAnywhere successfully", 200
    return "Unauthorized", 401

# ---------------------------
# Auth
# ---------------------------
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
        title="Login",
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
        ok = register_user(
            request.form["username"],
            request.form["password"]
        )
        if ok:
            return redirect(url_for("login"))
        error = "Benutzer existiert bereits."

    return render_template(
        "auth.html",
        title="Registrieren",
        action=url_for("register"),
        button_label="Registrieren",
        error=error,
        footer_text="Schon ein Konto?",
        footer_link_url=url_for("login"),
        footer_link_label="Login",
    )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ---------------------------
# INDEX / DASHBOARD
# ---------------------------
@app.route("/")
@login_required
def index():
    spiele = db_read(
        """
        SELECT
            s.spiel_id,
            ht.name AS heimteam,
            at.name AS auswaertsteam,
            s.tore_heimteam,
            s.tore_auswaertsteam
        FROM spiel s
        JOIN team ht ON s.heimteam_id = ht.id
        JOIN team at ON s.auswaertsteam_id = at.id
        WHERE ht.user_id = %s
        ORDER BY s.spiel_id DESC
        LIMIT 5
        """,
        (current_user.id,),
    ) or []

    return render_template("willkommen.html", letzte_spiele=spiele)

# ---------------------------
# SPIELE
# ---------------------------
@app.route("/spiele")
@login_required
def spiele():
    rows = db_read(
        """
        SELECT
            s.spiel_id,
            ht.name AS heimteam,
            at.name AS auswaertsteam,
            s.tore_heimteam,
            s.tore_auswaertsteam
        FROM spiel s
        JOIN team ht ON s.heimteam_id = ht.id
        JOIN team at ON s.auswaertsteam_id = at.id
        WHERE ht.user_id = %s
        ORDER BY s.spiel_id DESC
        """,
        (current_user.id,),
    ) or []

    return render_template("spiele.html", spiele=rows)

# ---------------------------
# SPIEL EINTRAGEN
# ---------------------------
@app.route("/spiel/eintragen", methods=["GET", "POST"])
@login_required
def spiel_eintragen():
    teams = db_read(
        "SELECT id, name FROM team WHERE user_id=%s ORDER BY name",
        (current_user.id,),
    ) or []

    if request.method == "GET":
        return render_template("spiel_eintragen.html", teams=teams, error=None)

    heim = int(request.form["heimteam_id"])
    aus = int(request.form["auswaertsteam_id"])

    if heim == aus:
        return render_template(
            "spiel_eintragen.html",
            teams=teams,
            error="Teams dürfen nicht gleich sein",
        )

    db_write(
        """
        INSERT INTO spiel (heimteam_id, auswaertsteam_id, tore_heimteam, tore_auswaertsteam)
        VALUES (%s, %s, %s, %s)
        """,
        (
            heim,
            aus,
            int(request.form["tore_heimteam"]),
            int(request.form["tore_auswaertsteam"]),
        ),
    )

    return redirect(url_for("spiele"))
