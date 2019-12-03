from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Command
from time import sleep
from app import app, db
from models import *

from app import calc_hash
from flask_sqlalchemy import SQLAlchemy

app.config['DEBUG'] = True

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:password@postgres:5432/postgres'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

migrate = Migrate(app, db)
manager = Manager(app)


class DemoStateCommand(Command):
    '''
        run /python manage.py db init
        -------
        run /python manage.py db upgrade
        run /python manage.py demostate
    '''
    def run(self):
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
            cert = Certificate()
            # cert.owner = man_with_certs
            cert.owner_id = man_with_certs.id
            db.session.add(cert)

        s_entry = ScheduleEntry()
        s_entry.name = "XMas event"
        s_entry.date = datetime.date(year=2019, month=12, day=25)
        s_entry.price = 40
        # s_entry.owner = man_with_event
        s_entry.owner_id = man_with_event.id

        db.session.add(s_entry)

        db.session.commit()


manager.add_command('db', MigrateCommand)

manager.add_command('demostate', DemoStateCommand())

if __name__ == "__main__":
    manager.run()
