from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Command
from time import sleep
from app import app, db
from models import *

from app import calc_hash
from app import invoke_user_buy_event

from flask_sqlalchemy import SQLAlchemy

app.config['DEBUG'] = True

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:password@postgres:5432/postgres'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

migrate = Migrate(app, db)
manager = Manager(app)


def PreTest():
    for model in (Session, Member, ScheduleEntry, Transaction, Certificate, Log):
        db.session.query(model).delete()
    db.session.commit()

    man_with_certs = Member("Alice", calc_hash("Alice_password"))
    man_with_certs.about = "Hello, my name is Alice! I have many certificates!"
    db.session.add(man_with_certs)

    man_with_event = Member("Bob", calc_hash("Bob_password"))
    man_with_event.about = "Hello! My name is Bob and I have Xmas event soon"
    db.session.add(man_with_event)

    db.session.commit()

    for _ in range(100):
        cert = Certificate(man_with_certs.id)
        db.session.add(cert)

    s_entry = ScheduleEntry(man_with_event.id, datetime.date(year=2019, month=12, day=25),
                            datetime.datetime(year=2019, month=12, day=25, hour=10), 40, "XMas event")

    db.session.add(s_entry)

    db.session.commit()


def TestBuy():
    PreTest()

    event_id = 1
    buyer_id = 1
    seller_id = 2

    schedule = db.session.query(ScheduleEntry).filter_by(id=event_id).first()
    buyer = db.session.query(Member).filter_by(id=buyer_id).first()
    seller = db.session.query(Member).filter_by(id=seller_id).first()


    assert db.session.query(Certificate).filter_by(owner_id=buyer.id).count() == 100
    assert db.session.query(ScheduleEntry).filter_by(owner_id=seller.id).first().buyer_id is None

    invoke_user_buy_event(buyer, seller, schedule)

    assert db.session.query(Certificate).filter_by(owner_id=buyer.id).count() == 60
    assert db.session.query(ScheduleEntry).filter_by(owner_id=seller.id).first().buyer_id == buyer_id


def TestDoubleBuy():
    PreTest()

    event_id = 1
    buyer_id = 1
    seller_id = 2

    schedule = db.session.query(ScheduleEntry).filter_by(id=event_id).first()
    buyer = db.session.query(Member).filter_by(id=buyer_id).first()
    seller = db.session.query(Member).filter_by(id=seller_id).first()


    assert db.session.query(Certificate).filter_by(owner_id=buyer.id).count() == 100
    assert db.session.query(ScheduleEntry).filter_by(owner_id=seller.id).first().buyer_id is None

    invoke_user_buy_event(buyer, seller, schedule)

    assert db.session.query(Certificate).filter_by(owner_id=buyer.id).count() == 60
    assert db.session.query(ScheduleEntry).filter_by(owner_id=seller.id).first().buyer_id == buyer_id



class TestsCommand(Command):
    def run(self):
        TestBuy()


class DemoStateCommand(Command):
    '''
        run /python manage.py db init
        -------
        run /python manage.py db upgrade
        run /python manage.py demostate
    '''
    def run(self):
        PreTest()


manager.add_command('db', MigrateCommand)

manager.add_command('demostate', DemoStateCommand())

manager.add_command('test', TestsCommand())

if __name__ == "__main__":
    # manager.run()
    TestBuy()
