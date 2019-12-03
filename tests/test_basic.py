import os
import unittest

from flask_sqlalchemy import SQLAlchemy

from app import app, calc_hash
from models import *

TEST_DB = 'app.db'


class BasicTests(unittest.TestCase):

    ############################
    #### setup and teardown ####
    ############################

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + TEST_DB

        db = SQLAlchemy(app)
        self.app = app.test_client()

        self.assertEqual(app.debug, False)

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

    # executed after each test
    def tearDown(self):
        pass

    ###############
    #### tests ####
    ###############

    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
