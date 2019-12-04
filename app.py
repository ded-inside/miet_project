from flask import Flask, jsonify, abort, render_template, make_response, redirect
from flask import request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import datetime


app = Flask(__name__)
app.config['DEBUG'] = True
app.debug = True
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:password@postgres:5432/postgres'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

db = SQLAlchemy(app)
from models import *

db.create_all()


def get_event_data(entry):
    owner = db.session.query(Member).filter_by(id=entry.owner_id).first()
    data = {"Owner": owner.login,
            "Id": entry.id,
            "DateTime": entry.date.strftime("%d/%m/%y %H:%M"),
            "Cost": entry.price,
            "Duration": entry.duration.strftime("%H:%M"),
            "Name": entry.name,
            "About": entry.about
            }
    return data


def get_public_member_data(mem):
    events = db.session.query(ScheduleEntry).filter_by(owner_id=mem.id, buyer_id=None).all()
    return dict(
        login=mem.login,
        about=mem.about,
        events=[
            get_event_data(e)
            for e in events
        ],
    )


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


@app.route("/", methods=['GET'])
def index():
    data = []
    members = db.session.query(Member).all()
    for m in members:
        data.append(get_public_member_data(m))
    print(data)
    cards = [{
        'name': 'Danny 1',
        'image_url': 'https://i.ytimg.com/vi/5EWp3vq5jlU/maxresdefault.jpg',
        'description': 'Cool guy'
    }, {
        'name': 'Danny 2',
        'image_url': 'https://avatars.mds.yandex.net/get-zen_doc/125920/pub_5d85ee7fd5bbc300add0a4fc_5d85eead74f1bc00ad2cb1c5/scale_1200',
        'description': 'Nice man!'
    }, {
        'name': 'Danny 3',
        'image_url': 'https://memepedia.ru/wp-content/uploads/2019/10/denni-de-vito-mem.png',
        'description': 'Ахахаха)'
    }, {
        'name': 'Danny 4',
        'image_url': 'https://img01.rl0.ru/afisha/1500x-/daily.afisha.ru/uploads/images/2/7f/27f7e31c0faf2dcd0c666849ba15e919.jpg',
        'description': 'Marry me!'
    }, {
        'name': 'Danny 5',
        'image_url': 'https://medialeaks.ru/wp-content/uploads/2019/05/yeah.jpg',
        'description': 'Рассо... Раса... Рамас... Рассол попил крч)0))'
    }]
    return render_template('index.html', current='index', cards=cards)


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html', current='login')

    json = request.form.to_dict()

    if not json:
        return abort(400)

    login = json["login"]
    pswd = json["password"]
    # remember = json["remember"]     # Null or "on" like false/true

    if not (login and pswd):
        return abort(400)

    member = db.session.query(Member).filter_by(login=login).first()
    if not member:
        return abort(400)

    if member.password_hash != calc_hash(pswd):
        return abort(400)

    sess = Session(calc_token(member.login + "secret_token"), datetime.datetime(year=2019, month=12, day=30))
    member.session = sess
    member.session_id = sess.id

    sess.token = calc_token(member.login + "secret_token")

    db.session.add(sess)

    db.session.commit()

    # return jsonify(code=200, token=sess.token)
    ret = make_response(redirect('/'))
    ret.set_cookie('token', sess.token)
    ret.set_cookie('username', member.login)
    return ret


@app.route("/<_login>")
def _login(_login: str):
    if not _login:
        return abort(400)

    member = db.session.query(Member).filter_by(login=_login).first()
    if not member:
        return abort(400)

    schedule_entries = db.session.query(ScheduleEntry).filter_by(owner_id=member.id).all()

    schedule_array = []
    for entry in schedule_entries:
        schedule_array.append({
            "Owner": _login,
            "Id": entry.id,
            "DateTime": entry.date.strftime("%d/%m/%y %H:%M"),
            "Cost": entry.price,
            "Duration": entry.duration.strftime("%H:%M"),
            "Name": entry.name,
            "About": entry.about
        })

    # return jsonify(code=200, data={"login": member.login, "about": member.about})
    return render_template('prof.html', user=member, shedules=schedule_array)


@app.route("/<_login>/schedule", methods=["GET"])
def _login_schedule(_login: str):
    if not _login:
        return abort(400)

    member = db.session.query(Member).filter_by(login=_login).first()
    if not member:
        return abort(400)

    schedule_entries = db.session.query(ScheduleEntry).filter_by(owner_id=member.id).all()

    schedule_array = []
    for entry in schedule_entries:
        schedule_array.append({
            "Owner": _login,
            "Id": entry.id,
            "DateTime": entry.date.strftime("%d/%m/%y %H:%M"),
            "Cost": entry.price,
            "Duration": entry.duration.strftime("%H:%M"),
            "Name": entry.name,
            "About": entry.about
        })

    return jsonify(
        code=200,
        data={
            "login": member.login,
            "schedule": schedule_array
        }
    )


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
    duration = datetime.datetime.strptime(duration, "%H:%M")

    se = ScheduleEntry(member.id, dt, duration, cost, name)

    db.session.add(se)

    db.session.commit()

    return jsonify(code=200, data={"id": se.id})


@app.route("/register", methods=['POST'])
def register():
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
        return jsonify(code=409, description="login is already taken")

    member = Member(login, password_hash)
    db.session.add(member)
    db.session.commit()
    return jsonify(code=200)


@app.route("/logout", methods=["POST"])
def logout():
    print(request)
    json = request.form.to_dict()
    print(json)
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

    # return jsonify(code=200)
    ret = make_response(redirect('/'))
    ret.set_cookie('token', '', max_age=0)
    ret.set_cookie('username', '', max_age=0)
    return ret


def invoke_user_buy_event(buyer, seller, schedule):
    certs = list(db.session.query(Certificate).filter_by(owner_id=buyer.id).all())

    if not (schedule.buyer_id is None):
        return "Already bought"

    trans_time = datetime.datetime.now()

    if len(certs) < schedule.price:
        return "Not enough certificates"

    for i in range(schedule.price):
        certs[i].owner_id = seller.id
        trns = Transaction(certs[i].id, seller.id, buyer.id, trans_time)
        db.session.add(trns)

    schedule.buyer_id = buyer.id

    db.session.commit()

    return None


@app.route("/<_login>/schedule/buy", methods=["POST"])
def login_schedule_buy(_login: str):
    json = request.form
    if not json:
        print('sched.buy: null')
        return abort(400)

    token = json["token"]
    if not token:
        print('sched.buy: no token')
        return abort(400)

    s_id = json["id"]
    if not s_id:
        print('sched.buy: no s_id')
        return abort(400)

    session = db.session.query(Session).filter_by(token=token).first()
    if not session:
        print('sched.buy: no session')
        return jsonify(code=403, description="Bad credentials")

    schedule = db.session.query(ScheduleEntry).filter_by(id=s_id).first()
    buyer = db.session.query(Member).filter_by(session=session).first()
    seller = db.session.query(Member).filter_by(login=_login).first()

    ret = invoke_user_buy_event(buyer, seller, schedule)
    if ret:
        return jsonify(code=100, description=ret)

    return jsonify(code=200)


@app.route("/transactions", methods=["POST", "GET"])
def transactions():
    json = request.form
    if not json:
        return abort(400)

    token = json["token"]
    if not token:
        return abort(400)

    member = get_member(token)
    if not member:
        return abort(400)

    trns_buy = db.session.query(Transaction.date_time, func.count(Transaction.date_time)).filter_by(
        from_id=member.id).group_by(Transaction.date_time).all()
    trns_sell = db.session.query(Transaction.date_time, func.count(Transaction.date_time)).filter_by(
        to_id=member.id).group_by(Transaction.date_time).all()

    data = {
        "Buy": [
            {
                "Amount": i[1],
                "Date": i[0]
            }
            for i in trns_buy
        ],
        "Sell": [
            {
                "Amount": i[1],
                "Date": i[0]
            }
            for i in trns_sell
        ]
    }

    return jsonify(code=200, data=data)


if __name__ == '__main__':
    print("LOL")
    app.run()
