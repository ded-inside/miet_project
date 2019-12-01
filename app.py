from flask import Flask, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask import request
import datetime


app = Flask(__name__)
app.config['DEBUG'] = True
app.debug = True
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:password@postgres:5432/postgres'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

db = SQLAlchemy(app)
from models import *

db.create_all()


def get_member(token: str):
    sess = db.session.query(Session).filter_by(token=token).first()
    if not sess:
        return None

    member = db.session.query(Member).filter_by(session_id=sess.id).first()

    return member


def calc_hash(pswd: str):
    return pswd[::-1]


def calc_token(data: str):
    return data


@app.route("/login", methods=['POST'])
def login():
    json = request.get_json()
    if not json:
        return abort(400)

    login = json["login"]
    pswd = json["password"]

    if not(login and pswd):
        return abort(400)

    member = db.session.query(Member).filter_by(login=login).first()
    if not member:
        return abort(400)

    if member.password_hash != calc_hash(pswd):
        return abort(400)

    sess = Session()
    member.session = sess
    member.session_id = sess.id

    sess.token = calc_token(member.login+"secret_token")

    db.session.add(sess)

    db.session.commit()

    return jsonify(code=200, token=sess.token)


@app.route("/certificates/send")
def certificates_send():
    return "kk"


@app.route("/<_login>")
def _login(_login: str):
    return jsonify(code=200, data={"login": "Member2", "about": "doing stuff for money"})


@app.route("/<_login>/schedule", methods=["GET"])
def _login_schedule(_login: str):
    return jsonify(code=200,
                   data={
                       "login": "xXvasyaXx",
                       "certificates_count": 123,
                       "schedule": [
                           {
                               "DateTime": "13:00 25.12.2019",
                               "Cost": 1,
                               "Duration": "01:00"
                           }
                       ]
                   })


@app.route("/<_login>/schedule/buy")
def _login_schedule_buy(_login: str):
    schedule_id = 1
    member = db.session.query(Member).filter_by(login=_login).first()
    if not member:
        return abort(400)

    return "iii"


@app.route("/schedule/add", methods=["POST", ])
def schedule_add():
    # "Sun, 24 Nov 2019 22:59:44 GMT"
    # '25/12/19 00:00'
    # "%d/%m/%y %H:%M"
    json = request.get_json()
    token = json["token"]
    member = get_member(token)
    if not member:
        abort(400)
    schedule = json["schedule"][0]
    name = schedule["Name"]
    dt = schedule["DateTime"]
    dt = datetime.datetime.strptime(dt, "%d/%m/%y %H:%M")
    # todo check if past

    cost = int(schedule["Cost"])
    # "Duration": "01:00",
    duration = schedule["Duration"]
    duration = datetime.datetime.strptime(duration,"%H:%M")

    se = ScheduleEntry()

    se.owner_id = member.id
    se.date = dt
    se.duration = duration
    se.price = cost
    se.name = name

    db.session.add(se)

    db.session.commit()


    return jsonify(code=200)


@app.route("/schedule/set")
def schedule_set():
    pass


@app.route("/logout")
def logout():
    pass


@app.route("/data/load")
def data_load():
    pass


@app.route("/add/user", methods=['POST'])
def add_member():
    json = request.get_json()
    if not json:
        return abort(400)

    login = json["login"]
    password = json["password"]

    if not login or not password:
        return abort(400)

    password_hash = password[::-1]

    member = db.session.query(Member).filter_by(login=login).first()
    if member is not None:
        return "login is already taken"

    member = Member(login, password_hash)
    db.session.add(member)
    db.session.commit()
    return "ok"


@app.route('/test1')
def hello_world():
    member = Member("test", "123")
    # member.password_hash = "123"
    db.session.add(member)
    db.session.commit()
    return "okokoko"


@app.route("/test2")
def test():

    return "ok"


if __name__ == '__main__':
    print("LOL")
    app.run()
@app.route('/login')
def login():
    return 'login'

@app.route("/logout", methods=["POST"])
def logout():
    json = request.get_json()
    if not json:
        return abort(400)

    token = json["token"]
    if not token:
        return abort(400)

    session = db.session.query(Session).filter_by(token=token).first()
    if not session:
        return jsonify(code=403, description="Bad credentials")
    db.session.delete(session)
    db.session.commit()

    return jsonify(code=200)


@app.route("/{login}/schedule/{s_id}/buy", methods=["POST"])
def login_schedule_buy(login: str, s_id: int):
    json = request.get_json()
    if not json:
        return abort(400)

    token = json["token"]
    if not token:
        return abort(400)

    session = db.session.query(Session).filter_by(token=token).first()
    if not session:
        return jsonify(code=403, description="Bad credentials")

    schedule = db.session.query(ScheduleEntry).filter_by(id=s_id)
    buyer = db.session.query(Member).filter_by(session=session).first()
    seller = db.session.query(Member).filter_by(login=login).first()
    certs = db.session.query(Certificate).filter_by(owner_id=buyer.id)

    if schedule.price > certs.count():
        return jsonify(code=100, description="Not enough certificates")

    for i in range(schedule.price):
        certs[i].owner_id = seller.id

    db.session.commit()
    return jsonify(code=200)









