import os
from pathlib import Path
import sqlalchemy.exc
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_httpauth import HTTPTokenAuth
from sqlalchemy.orm import relationship
import jwt
import uuid
import click

from passlib.context import CryptContext

Path("/data").mkdir(exist_ok=True)

pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=30000
)


app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:////data/auth.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = b'\x95\x19\x8ca\x9ei\x91\x13rO\xd9\xbct\xc2L\xa4\x1d4I\xad\x1e\x1c7?'
db = SQLAlchemy(app)

auth = HTTPTokenAuth(scheme='Bearer')


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    hashed_password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    sessions = relationship("Session")

    def set_password(self, password: str):
        self.hashed_password = pwd_context.encrypt(password)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

    def __str__(self):
        return f"{self.email} ({self.role}) {self.id}"


class Session(db.Model):
    __tablename__ = "session"
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("user.id"), nullable=False)


def encode_auth_token(user_id: str, session_id: str) -> str:
    try:
        payload = {
            'sub': user_id,
            "session": session_id
        }
        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return e


@auth.verify_token
def verify_token(token):
    try:

        payload = jwt.decode(token, app.config.get('SECRET_KEY'), algorithms=["HS256"])
    except jwt.exceptions.DecodeError:
        return None
    session = Session.query.filter_by(id=payload["session"]).first()
    if not session:
        return None

    user = User.query.filter_by(id=session.user_id).first()
    request.session = session
    return user


@auth.get_user_roles
def get_user_roles(user):
    return user.role


@app.route('/auth/login', methods=['POST'])
def login():
    body: dict = request.json
    if body is None:
        return "Bad request", 400

    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        return "Bad Request", 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.verify_password(password):
        return "User credentials not correct", 401

    session = Session(id=str(uuid.uuid4()), user_id=user.id)
    db.session.add(session)
    token = encode_auth_token(user.id, session.id)

    db.session.commit()

    return {
        "token": token
    }, 200


@app.route('/auth/logout', methods=["POST"])
@auth.login_required
def logout():
    Session.query.filter_by(id=request.session.id).delete()
    db.session.commit()
    return "", 200


@app.route('/auth/user', methods=["POST"])
@auth.login_required(role="admin")
def create_user():
    if not request.json:
        return "Invalid/missing parameters", 400

    email: str = request.json.get("email")
    password: str = request.json.get("password")
    role: str = request.json.get("role")

    if not email or not password or not role:
        return "Invalid/missing parameters", 400

    try:
        u = User(email=email, role=role, id=str(uuid.uuid4()))
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        return "Duplicate email", 400

    return "Created", 201


@app.route('/auth/user', methods=["GET"])
@auth.login_required(role="admin")
def get_users():
    print("get users")
    users = User.query.all()

    user_list = []
    for user in users:
        user_list.append({
            "id": user.id,
            "email": user.email,
            "role": user.role
        })

    return jsonify(user_list)


@app.route('/auth/user/<user_id>', methods=["GET"])
@auth.login_required
def get_user(user_id):
    if user_id == "self" or user_id == auth.current_user().id:
        return {
            "id": auth.current_user().id,
            "email": auth.current_user().email,
            "role": auth.current_user().role
        }, 200
    elif auth.current_user().role == "admin":
        user = User.query.filter_by(id=user_id).first()
        if user:
            return {
               "id": user.id,
               "email": user.email,
               "role": user.role
            }, 200

    if User.query.filter_by(id=user_id).first() is not None:
        return "Forbidden", 403

    return "Not Found", 404


@app.route('/auth/user/<user_id>', methods=["DELETE"])
@auth.login_required
def delete_user(user_id):
    if user_id == "self" or user_id == auth.current_user().id:
        User.query.filter_by(id=auth.current_user().id).delete()
        db.session.commit()
        return "Ok", 200
    elif auth.current_user().role == "admin":
        User.query.filter_by(id=user_id).delete()
        db.session.commit()
        return "Ok", 200

    if User.query.filter_by(id=user_id).first() is None:
        return "Not Found", 404
    return "Forbidden", 403


@app.route('/auth/test_reset', methods=["POST"])
def test_reset():
    testing = os.environ.get("INTEGRATION_TEST")
    if testing != "1":
        return "Not found", 404

    User.query.delete()
    Session.query.delete()
    db.session.commit()
    create_default_users()
    return "Ok", 200


def create_default_users():
    try:
        u = User(email="admin@example.com", role="admin", id=str(uuid.uuid4()))
        u.set_password("secret")
        db.session.add(u)

        u = User(email="provider@example.com", role="provider", id=str(uuid.uuid4()))
        u.set_password("secret")
        db.session.add(u)

        u = User(email="agent@example.com", role="agent", id=str(uuid.uuid4()))
        u.set_password("secret")
        db.session.add(u)
        db.session.commit()
    except Exception as e:
        pass

@app.cli.command("create-user")
@click.argument("email")
@click.argument("password")
@click.argument("role")
def create_user(email, password, role):
    print(email, password, role)

    u = User(email=email, role=role, id=str(uuid.uuid4()))
    u.set_password(password)
    db.session.add(u)
    db.session.commit()


@app.cli.command("list-users")
def list_users():
    users = User.query.all()
    for user in users:
        print(str(user))


@app.cli.command("delete-users")
def delete_users():
    User.query.delete()
    db.session.commit()


@app.cli.command("init-db")
def create_user():
    db.create_all()


@app.cli.command("create-default-users")
def create_default_users_from_cli():
    create_default_users()



if __name__ == '__main__':
    app.run()
