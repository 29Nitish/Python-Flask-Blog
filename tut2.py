import flask
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('index1.html')

@app.route('/about')
def greet():
    name = 'Nitish'
    return render_template('about1.html', name2=name)

@app.route('/bootstrap')
def bootstrap():
    return render_template('bootstrap.html')

@app.route('/bootstrap1')
def bootstrap1():
    return render_template('bootstrap1.html')

app.run(debug=True)