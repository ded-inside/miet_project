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
@app.route("/add/member", methods=['POST'])
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
    member = Member("test")
    member.password_hash = "123"
    db.session.add(member)
    db.session.commit()
    return "ok"


@app.route("/test2")
def test():
    a = Member.query.all()
    member = a[-1]
    return jsonify(login=member.login,id=member.id,pass_hash=member.password_hash)


if __name__ == '__main__':
    app.run()
