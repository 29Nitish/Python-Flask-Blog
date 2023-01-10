from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import os
from flask import jsonify
import os
import math
# import secrets

print(os.getcwd())

with open(r"D:\whtsapp\automation\API_part\flask_tut\config.json", 'r', encoding='utf8') as c:  
    params = json.load(c)["params"]
local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = params['upload_location']
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password']
)
mail = Mail(app)

if (local_server):
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_url'] # for making database connection
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_url']
db = SQLAlchemy(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text(50), nullable=False)
    phone_num = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DATETIME, nullable=True)
    msg = db.Column(db.Text, nullable=False)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    tagline = db.Column(db.Text, nullable=False)
    slug = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    img_file = db.Column(db.Text, nullable=False)
    date = db.Column(db.DATETIME, nullable=True)

@app.route('/')
def home():
    posts= Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))

    # posts = posts[]
    page = request.args.get('page')

    # page = int(request.args.get('number'))
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(params['no_of_posts']): (page-1)*int(params['no_of_posts']) + int(params['no_of_posts'])]   
    if (page==1):
        previous = "#"
        next = "/?page=" + str(page+1)
    elif (page==last):
        previous = "/?page" + str(page-1)
        next = "#"
    else:
        previous = "/?page" + str(page-1)
        next = "/page" + str(page+1)


    # posts= Posts.query.filter_by().all()[0: params['no_of_posts']]
    return render_template('index.html', params=params, posts=posts, prev=previous, next=next)

@app.route('/post/<string:post_slug>', methods=['GET', 'POST'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()

    # data_dict={
    #     "name":"albert",
    #     "job":"developer"
    # }
    # return jsonify(data_dict)
    return render_template('post.html', params=params, post=post)

@app.route('/about')
def about():
    return render_template('about.html', params=params)

@app.route('/dashboard', methods=['POST','GET'])
def dashboard():
    if ('user' in session and session['user'] == params['admin_user']):
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts=posts)

    if request.method=='POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        print(username,userpass)
        if(username == params['admin_user'] and userpass == params['password']):
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html', params=params, posts=posts)

    return render_template('login.html', params=params)

@app.route('/edit/<string:sno>', methods=['GET', 'POST'])
def edit(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            title = request.form.get('title')
            tagline = request.form.get('tagline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date=datetime.now()
            # print(title,tagline,"FDFD")

            if sno=='0':
                post=Posts(title=title, slug=slug, content=content,tagline=tagline, img_file=img_file, date=date)
                db.session.add(post)
                db.session.commit()
                return redirect('/edit/'+sno)

            else:
                post=Posts.query.filter_by(sno=sno).first()
                post.title = title
                post.slug = slug
                post.content=content
                post.tagline = tagline
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/dashboard')

        post = Posts.query.filter_by(sno=sno).first()

        return render_template('edit.html', params=params, post=post)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            title = request.form.get('title')
            tagline = request.form.get('tagline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date=datetime.now()
            post=Posts(title=title, slug=slug, content=content,tagline=tagline, img_file=img_file, date=date)
            db.session.add(post)
            db.session.commit()
            return redirect('/dashboard')
        return render_template('add.html', params=params)

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route('/delete/<string:sno>', methods=['GET', 'POST'])
def delete(sno):
    print(sno)
    if ('user' in session and session['user'] == params['admin_user']):
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')


@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if ('user' in session and session['user'] == params['admin_user']):
        if(request.method=='POST'):
            f = request.files['file1']
            # secure_filename=(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename) ))
            return "Uploaded Successfully"


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
        mail.send_message('New message from ' + name, 
                            sender=email, 
                            recipients=[params['gmail-user']],
                            body=message + "\n" + phone
                            )
        
    return render_template('contact.html', params=params)

@app.route('/post')
def post():
    return render_template('post.html')

app.run(debug=True)