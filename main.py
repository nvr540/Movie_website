from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename 
import json, datetime,time,os
app = Flask(__name__)
app.secret_key = 'super secret key'
params = json.load(open('config.json'))['params']
print(params)
app.config['SQLALCHEMY_DATABASE_URI'] = params['data_base_uri'] 
db = SQLAlchemy(app)
class Movies(db.Model): 
    sno = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(20), nullable=False) 
    slug =  db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(200), nullable=False)
    img_name =  db.Column(db.String(20), nullable=False)
    film_industry =  db.Column(db.String(20), nullable=False)
    date =  db.Column(db.String(20), nullable=False)
# slug =  db.Column(db.String(20), nullable=False)
@app.route("/")
def home():
    # movies = Movies.query.all()
    latest = Movies.query.order_by(Movies.date.desc()).limit(7).all()
    catagory = request.args.get('catagory') #Have to make catagory wise selection.
    if catagory == "film":
        action = Movies.query.filter_by(film_industry = 'anime').order_by(Movies.date.desc()).all()
        romance = Movies.query.filter_by(film_industry = 'hollywood').order_by(Movies.date.desc()).all()
        horror = Movies.query.filter_by(film_industry = 'bollywood').order_by(Movies.date.desc()).all()
        comedy = Movies.query.filter(Movies.film_industry != 'bollywood').filter(Movies.film_industry !='hollywood').filter(Movies.film_industry != 'anime').order_by(Movies.date.desc()).all()
        first_row,second_row, third_row, fourth_row = ["Anime","Hollywood","Bollywood","Others"]
    else:
        action = Movies.query.filter_by(genre='action').order_by(Movies.date.desc()).all()
        romance = Movies.query.filter_by(genre='romance').order_by(Movies.date.desc()).all()
        horror = Movies.query.filter_by(genre='horror').order_by(Movies.date.desc()).all()
        comedy = Movies.query.filter_by(genre='comedy').order_by(Movies.date.desc()).all()
        first_row,second_row, third_row, fourth_row = ["Action","Romance","Horror","Comedy"]
    return render_template("index.html",latest=latest, comedy=comedy,horror=horror, action=action,romance=romance, first_row = first_row, second_row = second_row, third_row=third_row, fourth_row=fourth_row)
@app.route("/movies/<string:slug>")
def movie_download(slug):
    movie = Movies.query.filter_by(slug=slug).first()
    return render_template("test.html", movie=movie)
@app.route("/movies")
def movies_vertical():
    # movies = Movies.query.all()
    # latest = Movies.query.order_by(Movies.date.desc()).limit(7).all()
    return render_template("movies_vertical.html")
@app.route("/dashboard", methods=['GET',  'POST'])
def dashboard():
    # if session['admin']== params['username'] and 'admin' in session:
    movies = Movies.query.all()
    if ('user' in session and session['user'] == params['username']):
        return render_template('dashboard.html', name='Admin Panel', movies=movies)
    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('pass')
        if username == params['username'] and password == params['password']:
            session['user'] = username
            return render_template('dashboard.html', name='Admin Panel', movies=movies)
    return redirect('/login')
#Editing name genre
@app.route('/dashboard/<string:sno>', methods=['GET', 'POST'])
def edit(sno):
    movie = Movies.query.filter_by(sno=sno).first()
    if session['user'] == params['username'] and 'user' in session:
        if request.method == 'GET':
            if sno == '0':
                return render_template("edit.html", movie=movie, sno=sno, img_name='s-1.jpg')
            else:
                return render_template("edit.html", movie=movie, sno=sno, img_name=movie.img_name)
        elif request.method == 'POST':
            name = request.form.get('name')
            slug = request.form.get('slug')
            description = request.form.get('description')
            genre = request.form.get('genre')
            film_industry = request.form.get('film_industry')
            global img_name
            img_name = request.form.get('img_name')

             #we could use f.filename instead of img_name As we are taking input from the user for the file name I didn't save with the filename uploading I am saving with the filename the user giving
            if sno== '0':
                post = Movies(name=name, slug=slug,
                            description=description, genre=genre,film_industry=film_industry, date=datetime.datetime.now(),img_name=img_name)
                db.session.add(post)
                db.session.commit()
            else:
                movie = Movies.query.filter_by(sno=sno).first()
                movie.name=name
                movie.slug=slug
                movie.description=description
                movie.genre=genre
                movie.film_industry=film_industry
                movie.img_name=img_name
                db.session.commit()
            time.sleep(2)
            return redirect('/dashboard')
    return redirect('/dashboard')
#Image uploader
@app.route('/uploader', methods=['POST'])
def uploader():
    if session['user'] == params['username'] and 'user' in session:
        if request.method == 'POST':
            f=request.files['files']
            f.save(os.path.join(params['path_upload'], secure_filename(img_name)))
    return redirect('/dashboard')
@app.route('/delete/<string:sno>')
def deleter(sno):
    if session['user'] == params['username'] and 'user' in session:
        post = Movies.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")
app.run(debug=True)