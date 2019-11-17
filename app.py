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

if __name__ == '__main__':
    print("LOL")
    app.run()
