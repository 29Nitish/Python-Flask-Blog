import flask
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime


# local_server = True
# with open('config.json', 'r') as c:
#     params = json.load(c)["params"]
# app = Flask(__name__)
# if (local_server):
#     app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri'] # for making database connection
# else:
#     app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_uri']
# db = SQLAlchemy(app)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:@localhost/codingthunder' # for making database connection
db = SQLAlchemy(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text(50), nullable=False)
    phone_num = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DATETIME, nullable=True)
    msg = db.Column(db.Text, nullable=False)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        ################## Add entry to the database #################
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        entry = Contacts(name=name, phone_num=phone, msg=message, date=datetime.now(), email=email)
        db.session.add(entry)
        db.session.commit()
        
    return render_template('contact.html')

@app.route('/post')
def post():
    return render_template('post.html')

app.run(debug=True)