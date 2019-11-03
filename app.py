from flask import Flask, jsonify, abort
from flask import render_template
# from flask_sqlalchemy import SQLAlchemy
from flask import request

app = Flask(__name__)

# app.config['DEBUG'] = True
# app.debug = True
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:password@postgres:5432/postgres'

# db = SQLAlchemy(app)

# from models import *
# db.create_all()


@app.route('/')
def index():

    return render_template('index.html')


@app.route('/username')
def username():

    user = { 'name': 'Dmitriy' }
    return render_template('index.html', user = user)


if __name__ == '__main__':
    app.run()
