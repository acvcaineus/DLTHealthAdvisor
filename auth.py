from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import Database

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get(user_id):
        db = Database()
        user = db.get_user_by_username(user_id)
        if user:
            return User(id=user['id'], username=user['username'], password_hash=user['password_hash'])
        return None

def create_user(username, password):
    db = Database()
    password_hash = generate_password_hash(password)
    return db.create_user(username, password_hash)

def authenticate_user(username, password):
    db = Database()
    user = db.get_user_by_username(username)
    if user and User(id=user['id'], username=user['username'], password_hash=user['password_hash']).check_password(password):
        return User(id=user['id'], username=user['username'], password_hash=user['password_hash'])
    return None
