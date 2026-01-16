import logging
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db import db_read, db_write

logger = logging.getLogger(__name__)
login_manager = LoginManager()


class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password = password_hash  # Flask-Login erwartet .password hier


    @staticmethod
    def get_by_id(user_id):
        logger.debug("User.get_by_id(%s)", user_id)
        row = db_read(
            "SELECT id, username, password_hash FROM users WHERE id=%s",
            (user_id,),
            single=True
        )
        if not row:
            logger.warning("Kein User mit id=%s", user_id)
            return None

        return User(row["id"], row["username"], row["password_hash"])


    @staticmethod
    def get_by_username(username):
        logger.debug("User.get_by_username(%s)", username)
        row = db_read(
            "SELECT id, username, password_hash FROM users WHERE username=%s",
            (username,),
            single=True
        )
        if not row:
            return None

        return User(row["id"], row["username"], row["password_hash"])


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.get_by_id(int(user_id))
    except Exception:
        logger.exception("load_user failed")
        return None


def register_user(username, password):
    if User.get_by_username(username):
        return False

    password_hash = generate_password_hash(password)
    db_write(
        "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
        (username, password_hash)
    )
    return True


def authenticate(username, password):
    user = User.get_by_username(username)
    if not user:
        return None

    if check_password_hash(user.password, password):
        return user

    return None
