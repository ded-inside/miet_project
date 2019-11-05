from flask import Flask, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask import request

app = Flask(__name__)
app.config['DEBUG'] = True
app.debug = True
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:password@postgres:5432/postgres'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

db = SQLAlchemy(app)
from models import *
db.create_all()


# """
#     login: string
#     password: string
#
#     return: token:string
# """
@app.route("/login")
def login():
    return jsonify(code=200, token="secret_token")


@app.route("/certificates/send")
def certificates_send():
    pass



@app.route("/<login>")
def _login(login: str):
    pass


@app.route("/<login>/schedule")
def _login_schedule(login: str):
    pass


@app.route("/<login>/schedule/buy")
def _login_schedule_buy(login: str):
    pass


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
    a = Member.query.all()
    member = a[-1]
    return jsonify(login=member.login,id=member.id,pass_hash=member.password_hash)


if __name__ == '__main__':
    Member.query.delete()
    app.run()
