
from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.orm import relationship
import requests
import uuid

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:////tmp/data/job.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = b'\x95\x19\x8ca\x9ei\x91\x13rO\xd9\xbct\xc2L\xa4\x1d4I\xad\x1e\x1c7?'
db = SQLAlchemy(app)
AUTH_HOST = "auth"

class Job(db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.Integer, primary_key=True)
    pickup_at = db.Column(db.String, nullable=False)
    pickup_geo = db.Column(db.String, nullable=False)
    deliver_at = db.Column(db.String, nullable=False)
    deliver_geo = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    agent_user_id = db.Column(db.String, nullable=True)
    provider_user_id = db.Column(db.String, nullable=False)
    job_id = db.Column(db.String, nullable=False)

    def __str__(self):
        return f'"pickup_at": "{self.pickup_at}", \
                    "deliver_at": "{self.deliver_at}", \
                    "description": "{self.description}", \
                    "status": "{self.status}", \
                    "agent_user_id": "{self.agent_user_id}", \
                    "provider_user_id": "{self.provider_user_id}", \
                    "job_id": "{self.job_id}"'

def authorize(header):
    bearer = header.get('Authorization')
    token = bearer.split()[1]
    headers = { "Authorization": "Bearer {0}".format(token)}
    return requests.get("http://{0}:5000/auth/user/self".format(AUTH_HOST), headers=headers)


@app.route('/job', methods=['POST'])
def create_job():
    token = ""
    r = None
    try:
        r = authorize(request.headers)
    except Exception as e:
        print(str(e))
        return "Access token is missing or invalid", 401

    if r.status_code != 200:
        return "Access token is missing or invalid", 401

    if r.json()["role"] not in ["provider", "admin"]:
        return "User is not permitted to perform this operation (e.g. wrong role)", 403

    body: dict = request.json
    pickup_at = body.get("pickup_at")
    deliver_at = body.get("deliver_at")
    description = body.get("description")

    if not pickup_at or not deliver_at or not description:
        return "Invalid parameters", 400

    jid = str(uuid.uuid4())

    j = Job(pickup_at=pickup_at,
            pickup_geo="todo",
            deliver_at=deliver_at,
            deliver_geo="todo",
            description=description,
            status='open',
            agent_user_id=None,
            provider_user_id=str(r.json()["id"]),
            job_id=jid)

    db.session.add(j)
    db.session.commit()

    return ("Job successfully created", 201, {"Location" : "/job/{0}".format(jid)})


@app.route('/job', methods=['GET'])
def get_jobs():
    token = ""
    r = None
    try:
        r = authorize(request.headers)
    except Exception as e:
        print(str(e))
        return "Access token is missing or invalid", 401

    if r.status_code != 200:
        return "Access token is missing or invalid", 401

    f_radius = None
    f_long = None
    f_lat = None
    f_state = None
    f_provider_user_id = None
    f_agend_user_id = None

    body: dict = request.json

    if r.json()["role"] in ["admin", "agent"]:
        f_radius = body.get("radius")
        f_long = body.get("longitude")
        f_lat = body.get("latitude")
    
    if r.json()["role"] in ["admin", "agent", "provider"]:
        f_status = body.get("status")

    if r.json()["role"] == "admin":
        f_provider_user_id = body.get("provider_user_id")
        f_agend_user_id = body.get("agent_user_id")

    if r.json()["role"] == "provider":
        f_provider_user_id = "self"

    if r.json()["role"] == "agent":
        f_agend_user_id = "self"

    # Todo: continue

    #Job.query.filter_by(id=user_id).delete()

    return "todo", 401


@app.route('/job/<job_id>', methods=['GET'])
def get_job_info(job_id):
    if not job_id:
        return "Invalid Paramter", 404 # todo: add in swagger

    token = ""
    r = None
    try:
        r = authorize(request.headers)
    except Exception as e:
        print(str(e))
        return "Access token is missing or invalid", 401

    if r.status_code != 200:
        return "Access token is missing or invalid", 401

    if r.json()["role"] not in ["provider", "admin", "agent"]:
        return "User is not permitted to perform this operation (e.g. wrong role)", 403

    j = Job.query.filter_by(job_id=job_id).first()

    if j is None:
        return "Job not found", 404

    return str(j), 200


@app.route('/job/<job_id>', methods=['PUT'])
def update_job(job_id):
    if not job_id:
        return "Invalid parameters", 400

    token = ""
    r = None
    try:
        r = authorize(request.headers)
    except Exception as e:
        print(str(e))
        return "Access token is missing or invalid", 401

    if r.status_code != 200:
        return "Access token is missing or invalid", 401

    if r.json()["role"] not in ["admin", "agent"]:
        return "User is not permitted to perform this operation (e.g. wrong role)", 403

    j = Job.query.filter_by(job_id=job_id).first()

    if j is None:
        return "Job not found", 404
        
    body: dict = request.json

    if not body.get("pickup_at") or not body.get("deliver_at") \
        or not body.get("description") or not body.get("status") \
        or not body.get("agent_user_id"):
        return "Invalid parameters", 400

    j.pickup_at = body.get("pickup_at")
    j.deliver_at = body.get("deliver_at")
    j.description = body.get("description")
    j.status = body.get("status")
    j.agent_user_id = body.get("agent_user_id")
    j.pickup_geo = "todo"
    j.deliver_geo = "todo"
    db.session.commit()

    return "Job successfully updated", 200


@app.route('/job/tracking/<job_id>', methods=['GET'])
def track_job(job_id):
    if not job_id:
        return "Job not found", 404

    j = Job.query.filter_by(job_id=job_id).first()

    if j is None:
        return "Job not found", 404

    # Todo: add agent tracking information
    return str(j), 200


@app.cli.command("init-db")
def create_tables():
    db.create_all()


if __name__ == '__main__':
    db.create_all()
    db.session.commit()
    app.run()
