import sys

sys.path.extend("..")
import json
import os
import unittest

from flask import jsonify
from flask_sqlalchemy import SQLAlchemy

from app import app, calc_hash

from models import *

TEST_DB = 'app.db'


class FronendTests(unittest.TestCase):

    ########################
    #### helper methods ####
    ########################

    def register(self, login, password):
        return self.app.post("/register",
                             data=json.dumps(dict(login=login, password=password)),
                             content_type='application/json'
                             )

    def login(self, login, password):
        return self.app.post("/login",
                             data=json.dumps(dict(login=login, password=password)),
                             content_type='application/json'
                             )

    def loginGetToken(self, login, password):
        response = self.login(login, password)
        _json = response.get_json()
        return _json["token"]

    def logout(self, token):
        return self.app.post("/logout",
                             data=json.dumps(dict(token=token, )),
                             content_type='application/json'
                             )

    def assertCodeEqual(self, response, code):
        _json = response.get_json()
        self.assertIsNotNone(_json)
        self.assertIn("code", _json)
        self.assertEqual(_json["code"], code)

    def assertDescriptionEqual(self, response, description):
        _json = response.get_json()
        self.assertIsNotNone(_json)
        self.assertIn("description", _json)
        self.assertEqual(_json["description"], description)

    def buy_event(self, token, seller, _id):
        return self.app.post(f"/{seller}/schedule/{_id}/buy",
                             data=json.dumps(dict(token=token)),
                             content_type='application/json'
                             )

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

    def test_login(self):
        response = self.login("Alice", "Alice_password")
        _json = response.get_json()
        self.assertIsNotNone(_json)
        self.assertIn("token", _json)
        self.assertEqual(response.status_code, 200)

    def test_login_incorrect(self):
        response = self.login("Alice", "Bad_password")
        self.assertEqual(response.status_code, 400)

    def test_logout(self):
        token = self.loginGetToken("Alice", "Alice_password")
        response = self.logout(token)

        self.assertCodeEqual(response, 200)

    def test_logout_incorrect_token(self):
        token = self.loginGetToken("Alice", "Alice_password")
        response = self.logout("Not" + token)

        self.assertCodeEqual(response, 403)
        self.assertDescriptionEqual(response, "Bad credentials")

    def test_cant_get_info_after_logout(self):
        pass

    def test_register_new_user(self):
        response = self.register("NewUser", "NewUser_password")
        self.assertEqual(response.status_code, 200)

    def test_register_new_user_with_existing_name(self):
        response = self.register("Alice", "NewUser_password")
        self.assertCodeEqual(response, 409)

    def test_add_new_event(self):
        response = self.login("Alice", "Alice_password")
        _json = response.get_json()
        token = _json["token"]
        response = self.app.post("/schedule/add",
                                 data=json.dumps(dict(token=token, schedule=[
                                     {
                                         "DateTime": '25/12/19 00:00',
                                         "Cost": 123,
                                         "Duration": "01:00",
                                         "Name": "XMAS event"
                                     }
                                 ])),
                                 content_type='application/json'
                                 )
        self.assertCodeEqual(response, 200)
        _json = response.get_json()
        self.assertDictEqual(_json["data"], dict(id=2))

    def test_buy_event(self):
        token = self.loginGetToken("Alice", "Alice_password")
        response = self.app.post("/Bob/schedule/1/buy",
                                 data=json.dumps(dict(token=token)),
                                 content_type='application/json'
                                 )

        self.assertCodeEqual(response, 200)

    def test_buy_event_with_not_enough_certificates(self):
        self.register("NewUser", "NewUser_password")
        token = self.loginGetToken("NewUser", "NewUser_password")
        response = self.app.post("/Bob/schedule/1/buy",
                                 data=json.dumps(dict(token=token)),
                                 content_type='application/json'
                                 )
        self.assertCodeEqual(response, 100)
        self.assertDescriptionEqual(response, "Not enough certificates")

    def test_buy_already_bought_event(self):
        token = self.loginGetToken("Alice", "Alice_password")
        self.buy_event(token, "Bob", 1)

        response = self.buy_event(token, "Bob", 1)

        self.assertCodeEqual(response, 100)
        self.assertDescriptionEqual(response, "Already bought")

    def test_get_schedule(self):
        response = self.app.get('/Bob/schedule', follow_redirects=True)
        self.assertCodeEqual(response, 200)
        ideal = {'login': 'Bob',
                 'schedule': [{"owner": "Bob", "id": 1, 'Cost': 40, 'DateTime': '25/12/19 00:00', 'Duration': '10:00'}]}
        self.assertDictEqual(response.get_json()["data"], ideal)

    def test_transaction(self):
        token = self.loginGetToken("Alice", "Alice_password")

        self.buy_event(token, "Bob", 1)

        response = self.app.post("/transactions",
                                 data=json.dumps(dict(token=token)),
                                 content_type='application/json'
                                 )
        # todo fix date
        ideal = {'Buy': [], 'Sell': [{'Amount': 40, 'Date': ""}]}
        _json = response.get_json()
        _json["data"]["Sell"][0]["Date"] = ""

        self.assertDictEqual(ideal, _json["data"])

        token = self.loginGetToken("Bob", "Bob_password")

        ideal = {'Sell': [], 'Buy': [{'Amount': 40, 'Date': ""}]}
        response = self.app.post("/transactions",
                                 data=json.dumps(dict(token=token)),
                                 content_type='application/json'
                                 )

        _json = response.get_json()
        _json["data"]["Buy"][0]["Date"] = ""

        self.assertDictEqual(ideal, _json["data"])


if __name__ == "__main__":
    unittest.main()
