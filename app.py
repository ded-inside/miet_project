from flask import Flask, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask import request
from datetime import datetime


app = Flask(__name__)
app.config['DEBUG'] = True
app.debug = True
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:password@postgres:5432/postgres'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

db = SQLAlchemy(app)
from models import *

db.create_all()

@app.route("/login")
def login():
    return jsonify(code=200, token="secret_token")


@app.route("/certificates/send")
def certificates_send():
    m1 = db.session.query(Member).filter_by(id=1).first()
    m2 = db.session.query(Member).filter_by(id=2).first()
    certs = db.session.query(Certificate).filter_by(owner_id=m1.id)
    for i in range(certs.count() // 2):
        certs[i].owner_id = m2.id

    db.session.commit()
    return "kk"


@app.route("/<_login>")
def _login(_login: str):
    return jsonify(code=200, data={"login": "Member2", "about": "doing stuff for money"})


@app.route("/<_login>/schedule", methods=["GET"])
def _login_schedule(_login: str):
    # sched = db.session.query(Schedule).join(Member).filter_by(login=_login).first()
    # if not sched:
    #     return "no schedule"

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


@app.route("/<login>/schedule/buy")
def _login_schedule_buy(login: str):
    schedule_id = 1
    member = db.session.query(Member).filter_by(login=login).first()
    if not member:
        return abort(400)

    return "iii"


@app.route("/schedule/add")
def schedule_add():
    pass


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

    # todo add hash generation
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
