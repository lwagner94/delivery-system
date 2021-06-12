
from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_cors import CORS
from sqlalchemy.orm import relationship
import requests
import uuid
import math
from pathlib import Path
import os

Path("/data").mkdir(exist_ok=True)

app = Flask(__name__)
CORS(app)
#app.config["SERVER_NAME"] = "localhost:8000"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:////data/job.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = b'\x95\x19\x8ca\x9ei\x91\x13rO\xd9\xbct\xc2L\xa4\x1d4I\xad\x1e\x1c7?'
db = SQLAlchemy(app)

AUTH_HOST = "auth"
AUTH_PORT = "5000"

GEO_HOST = "geo"
GEO_PORT = "80"

class Job(db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.Integer, primary_key=True)
    pickup_at = db.Column(db.String, nullable=False)
    pickup_lon = db.Column(db.Numeric(3,15), nullable=False)
    pickup_lat = db.Column(db.Numeric(3,15), nullable=False)
    deliver_at = db.Column(db.String, nullable=False)
    deliver_lon = db.Column(db.Numeric(3,15), nullable=False)
    deliver_lat = db.Column(db.Numeric(3,15), nullable=False)
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


def authorize(token):
    if AUTH_HOST is None or AUTH_PORT is None:
        return None
    headers = { "Authorization": "Bearer {0}".format(token)}
    return requests.get("http://{0}:{1}/auth/user/self".format(AUTH_HOST, AUTH_PORT), headers=headers)


def geolocate(address, token):
    print("In geo", flush=True)
    
    if GEO_HOST is None or GEO_PORT is None:
        return None
    headers = { "Authorization": "Bearer {0}".format(token)}

    lon = None
    lat = None

    try:
        params = {
            "address": address
        }

        r = requests.get("http://{0}:{1}/geo/coordinates".format(GEO_HOST, GEO_PORT), headers=headers, params=params)

        if r.status_code != 200:
            return None

        lon = r.json()["longitude"]
        lat = r.json()["latitude"]
    except Exception as e:
        print(e, flush=True)
        return None

    return (lon, lat)


# SQLITE functions
def distance(pickup_lat, pickup_lon, f_lat, f_lng):
    return 1000 * 6371 * math.acos(
            math.cos(math.radians(f_lat)) 
            * math.cos(math.radians(pickup_lat))
            * math.cos(math.radians(pickup_lon) - math.radians(f_lng)) 
            + math.sin(math.radians(f_lat))
            * math.sin(math.radians(pickup_lat)))


@app.route('/job', methods=['POST'])
def create_job():
    token = ""
    r = None
    try:
        token = request.headers.get('Authorization').split()[1]
        print(token)
        r = authorize(token)
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

    (pu_lon, pu_lat) = geolocate(pickup_at, token)
    (d_lon, d_lat) = geolocate(deliver_at, token)

    if pu_lat is None or pu_lon is None or d_lon is None or d_lat is None:
        return "Invalid parameters", 400

    j = Job(pickup_at=pickup_at,
            pickup_lon=pu_lon,
            pickup_lat=pu_lat,
            deliver_at=deliver_at,
            deliver_lon=d_lon,
            deliver_lat=d_lat,
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
        token = request.headers.get('Authorization').split()[1]
        r = authorize(token)
    except Exception as e:
        print(str(e))
        return "Access token is missing or invalid", 401

    if r is None or r.status_code != 200:
        return "Access token is missing or invalid", 401

    f_radius = None
    f_long = None
    f_lat = None
    f_status = None
    f_provider_user_id = None
    f_agend_user_id = None

    body: dict = request.json

    if r.json()["role"] in ["admin", "agent"]:
        f_radius = float(body.get("radius"))
        f_long = float(body.get("longitude"))
        f_lat = float(body.get("latitude"))
    
    if r.json()["role"] in ["admin", "agent", "provider"]:
        f_status = body.get("status")

    if r.json()["role"] == "admin":
        f_provider_user_id = body.get("provider_user_id")
        f_agend_user_id = body.get("agent_user_id")

    if r.json()["role"] == "provider":
        f_provider_user_id = "self"

    if r.json()["role"] == "agent":
        f_agend_user_id = "self"

    #f_sql_status = "" if f_status is None else "AND status = '{0}'".format(f_status)
    #f_sql_agend_user_id = "" if f_agend_user_id is None else "AND agent_user_id = '{0}'".format(f_agend_user_id)
    #f_sql_provider_user_id = "" if f_provider_user_id is None else "AND provider_user_id = '{0}'".format(f_provider_user_id)

    #sql_statement = " SELECT id,  distance(...)\
    #        FROM jobs \
    #        WHERE (1=1 {3} {4} {5} ) \
    #        HAVING distance < {2} \
    #        ORDER BY distance;".format(f_lat, f_long, f_radius, f_sql_status, f_sql_agend_user_id, f_sql_provider_user_id)
    #result = db.engine.execute(sql_statement)

    # Todo: SQLAlchemy in combination with sqlite3.create_function causes troubles!
    #       solves this issue to get a much better runtime

    if f_radius is not None and (f_lat is None or f_long is None):
        return "Invalid Paramter", 404 

    j = Job.query

    if f_status is not None:
        j = j.filter_by(status=f_status)

    if f_agend_user_id is not None:
        j = j.filter_by(agent_user_id=f_agend_user_id)

    if f_provider_user_id is not None:
        j = j.filter_by(provider_user_id=f_provider_user_id)

    # pre-filter square
    if f_radius is not None:
        d_lat = abs((180/math.pi) * (f_radius/6378137))
        d_long = abs((180/math.pi) * (f_radius/6378137) / math.cos(f_lat))
        j = j.filter(Job.pickup_lat >= f_lat - d_lat, Job.pickup_lat <= f_lat + d_lat);
        j = j.filter(Job.pickup_lon >= f_long - d_long, Job.pickup_lon <= f_long + d_long);

    jobs = j.all()
    
    # fine-filter
    if f_radius is not None:
        for item in list(jobs):
            if distance(item.pickup_lat, item.pickup_lon, f_lat, f_long) > f_radius:
                jobs.remove(item)
    
    # print as list
    json_lst = "["
    for j in list(jobs):
        json_lst += " {" + str(j) + "},"

    json_lst = json_lst.rstrip(",")
    json_lst += "]"

    return json_lst, 200


@app.route('/job/<job_id>', methods=['GET'])
def get_job_info(job_id):
    if not job_id:
        return "Invalid Paramter", 404 # todo: add in swagger

    token = ""
    r = None
    try:
        token = request.headers.get('Authorization').split()[1]
        r = authorize(token)
    except Exception as e:
        print(str(e))
        return "Access token is missing or invalid", 401

    if r is None or r.status_code != 200:
        return "Access token is missing or invalid", 401

    if r.json()["role"] not in ["provider", "admin", "agent"]:
        return "User is not permitted to perform this operation (e.g. wrong role)", 403

    j = Job.query.filter_by(job_id=job_id).first()

    if j is None:
        return "Job not found", 404

    return {
        "pickup_at": j.pickup_at,
        "deliver_at": j.deliver_at,
        "description": j.description,
        "status": j.status,
        "agent_user_id": j.agent_user_id,
        "provider_user_id": j.provider_user_id,
        "job_id": j.job_id
    }, 200


@app.route('/job/<job_id>', methods=['PUT'])
def update_job(job_id):
    if not job_id:
        return "Invalid parameters", 400

    token = ""
    r = None
    try:
        token = request.headers.get('Authorization').split()[1]
        r = authorize(token)
    except Exception as e:
        print(str(e))
        return "Access token is missing or invalid", 401

    if r is None or r.status_code != 200:
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

    (pu_lon, pu_lat) = geolocate(body.get("pickup_at"), token)
    (d_lon, d_lat) = geolocate(body.get("deliver_at"), token)

    if pu_lon is None or pu_lat is None or d_lon is None or d_lat is None:
        return "Invalid parameters", 400

    j.pickup_at = body.get("pickup_at")
    j.deliver_at = body.get("deliver_at")
    j.description = body.get("description")
    j.status = body.get("status")
    j.agent_user_id = body.get("agent_user_id")
    j.pickup_lon = pu_lon
    j.pickup_lat = pu_lat
    j.deliver_lon = d_lon
    j.deliver_lat = d_lat
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
    return {
        "pickup_at": j.pickup_at,
        "deliver_at": j.deliver_at,
        "description": j.description,
        "status": j.status,
        "longitude": "",
        "latitude": ""
    }, 200

@app.route('/job/test_reset', methods=["POST"])
def test_reset():
    testing = os.environ.get("INTEGRATION_TEST")
    if testing != "1":
        return "Not found", 404

    Job.query.delete()
    db.session.commit()
    return "Ok", 200


@app.cli.command("init-db")
def create_tables():
    db.create_all()


if __name__ == '__main__':
    db.create_all()
    db.session.commit()
    app.run()
