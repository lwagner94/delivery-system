
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.orm import relationship

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:////tmp/data/job.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = b'\x95\x19\x8ca\x9ei\x91\x13rO\xd9\xbct\xc2L\xa4\x1d4I\xad\x1e\x1c7?'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.String, primary_key=True)
    pickup_at = db.Column(db.String, nullable=False)
    deliver_at = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    agent_user_id = db.Column(db.String, nullable=False)
    provider_user_id = db.Column(db.String, nullable=False)
    job_id = db.Column(db.String, nullable=False)

    def __str__(self):
        return f"{self.id} {self.job_id} {self.description} {self.status}"


@app.route('/job/', methods=['POST'])
def login():
    token = ""
    try:
        bearer = request.headers.get('Authorization')
        token = request.bearer.split()[1]
    except:
        return "Access token is missing or invalid", 401

    body: dict = request.json

    pickup_at = body.get("pickup_at")
    deliver_at = body.get("deliver_at")
    description = body.get("description")

    if not pickup_at or not deliver_at or not description:
        return "Invalid parameters", 400


    #user = User.query.filter_by(email=email).first()

    return "Job successfully created", 201


if __name__ == '__main__':
    app.run()
