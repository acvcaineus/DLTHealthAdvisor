from werkzeug.security import generate_password_hash, check_password_hash
from database import Database

class User:
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get(user_id):
        db = Database()
        user_data = db.get_user_by_id(user_id)
        if user_data:
            return User(id=user_data['id'], username=user_data['username'], password_hash=user_data['password_hash'])
        return None

    @staticmethod
    def get_by_username(username):
        db = Database()
        user_data = db.get_user_by_username(username)
        if user_data:
            return User(id=user_data['id'], username=user_data['username'], password_hash=user_data['password_hash'])
        return None

def create_user(username, password):
    db = Database()
    password_hash = generate_password_hash(password)
    user_id = db.create_user(username, password_hash)
    if user_id:
        return user_id
    return None

def authenticate_user(username, password):
    user = User.get_by_username(username)
    if user and user.check_password(password):
        return user
    return None
