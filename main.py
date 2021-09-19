from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import json
import datetime
import time
import os
import math
app = Flask(__name__)
app.secret_key = 'super secret key'
params = json.load(open('config.json'))['params']
# print(params)
app.config['SQLALCHEMY_DATABASE_URI'] = params['data_base_uri']
db = SQLAlchemy(app)


class Movies(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    slug = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(200), nullable=False)
    img_name = db.Column(db.String(20), nullable=False)
    film_industry = db.Column(db.String(20), nullable=False)
    meta_description = db.Column(db.String(20), nullable=False)
    meta_keywords = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(20), nullable=False)
# slug =  db.Column(db.String(20), nullable=False)


@app.route("/")
def home():
    # movies = Movies.query.all()
    latest = Movies.query.order_by(Movies.date.desc()).limit(7).all()
    # Have to make catagory wise selection.
    catagory = request.args.get('catagory')
    if catagory == "film":
        action = Movies.query.filter_by(
            film_industry='anime').order_by(Movies.date.desc()).all()
        romance = Movies.query.filter_by(
            film_industry='hollywood').order_by(Movies.date.desc()).all()
        horror = Movies.query.filter_by(
            film_industry='bollywood').order_by(Movies.date.desc()).all()
        comedy = Movies.query.filter(Movies.film_industry != 'bollywood').filter(
            Movies.film_industry != 'hollywood').filter(Movies.film_industry != 'anime').order_by(Movies.date.desc()).all()
        first_row, second_row, third_row, fourth_row = [
            "Anime", "Hollywood", "Bollywood", "Others"]
    else:
        action = Movies.query.filter_by(
            genre='action').order_by(Movies.date.desc()).all()
        romance = Movies.query.filter_by(
            genre='romance').order_by(Movies.date.desc()).all()
        horror = Movies.query.filter_by(
            genre='horror').order_by(Movies.date.desc()).all()
        comedy = Movies.query.filter_by(
            genre='comedy').order_by(Movies.date.desc()).all()
        first_row, second_row, third_row, fourth_row = [
            "Action", "Romance", "Horror", "Comedy"]
    return render_template("index.html", latest=latest, comedy=comedy, horror=horror, action=action, romance=romance, first_row=first_row, second_row=second_row, third_row=third_row, fourth_row=fourth_row)


@app.route("/movies/download/<string:slug>")
def movie_download(slug):
    movie = Movies.query.filter_by(slug=slug).first()
    return render_template("test.html", movie=movie)

"""Vertically movies display"""
@app.route("/movies/<string:genre>")
def movies_vertical(genre):
    movies = Movies.query.all()
    # movies = Movies.query.filter_by(genre=genre).order_by(Movies.date.desc()).limit(7).all()
    return render_template("movies_vertical.html", movies=movies)


"""Dash Board"""


@app.route("/dashboard", methods=['GET',  'POST'])
def dashboard():
    movies = Movies.query.order_by(Movies.date.desc()).all()
    # [0:params['no_of_post']]
    page = request.args.get('page')
    last = math.ceil(len(movies)/int(params['no_of_movies']))
    # print(last)
    # print(page)
    display_priv = '#'
    display_next = '#'
    if str(page).isnumeric() != True:
        page = 1
    elif int(page) > last or int(page) < 1:
        page = 1
    if int(page) == 1:
        priv = '#'
        next = int(page) + 1
        display_priv = "display:none;"
    elif int(page) == last:
        next = '#'
        display_next = "display:none;"
        priv = int(page) - 1
    else:
        priv = int(page) - 1
        next = int(page) + 1
    movies = movies[(int(page)-1) * params['no_of_movies']
                     :int(page)*params['no_of_movies']]
    if ('user' in session and session['user'] == params['username']):
        return render_template('dashboard.html', name='Admin Panel', movies=movies, priv=priv, next=next, display_next=display_next, display_priv=display_priv)
    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('pass')
        if username == params['username'] and password == params['password']:
            session['user'] = username
            return render_template('dashboard.html', name='Admin Panel', movies=movies)
    return redirect('/login')
# Editing name genre


@app.route('/dashboard/<string:sno>', methods=['GET', 'POST'])
def edit(sno):
    movie = Movies.query.filter_by(sno=sno).first()
    if session['user'] == params['username'] and 'user' in session:
        if request.method == 'GET':
            if sno == '0':
                return render_template("Add.html", movie=movie, sno=sno, img_name='s-1.jpg')
            else:
                return render_template("edit.html", movie=movie, sno=sno, img_name=movie.img_name)
        elif request.method == 'POST':
            name = request.form.get('name')
            slug = request.form.get('slug')
            description = request.form.get('description')
            genre = request.form.get('genre').lower()
            film_industry = request.form.get('film_industry').lower()
            global image_name
            image_name = request.form.get("img_name")#This global variable will go to /uploader

            # we could use f.filename instead of img_name As we are taking input from the user for the file name I didn't save with the filename uploading I am saving with the filename the user giving
            if sno == '0':
                post = Movies(name=name, slug=slug,
                              description=description, genre=genre, film_industry=film_industry, date=datetime.datetime.now(), img_name=image_name)
                db.session.add(post)
                db.session.commit()
            else:
                movie = Movies.query.filter_by(sno=sno).first()
                movie.name = name
                movie.slug = slug
                movie.description = description
                movie.genre = genre
                movie.film_industry = film_industry
                movie.img_name = image_name
                db.session.commit()
            time.sleep(2)
            return redirect('/dashboard')
    return redirect('/dashboard')
# SEO


@app.route("/seo/<string:sno>", methods=["GET","POST"])
def seo_links(sno):
    movies = Movies.query.filter_by(sno=sno).first()
    if request.method == "GET":
        if sno == "0":
            img_name = "s-1.jpg"
            meta_keywords = ''
            meta_description = ''
        else:
            img_name = movies.img_name
            meta_description = movies.meta_description
            meta_keywords = movies.meta_keywords
        return render_template("seo_edit.html", meta_description=meta_description, meta_keywords=meta_keywords, img_name=img_name,sno=sno)
    elif request.method =="POST":
        meta_description = request.form.get('meta_description')
        meta_keywords = request.form.get('meta_keywords')
        movies.meta_description = meta_description
        movies.meta_keywords = meta_keywords
        db.session.commit()
        return redirect("/dashboard")

# Image uploader
image_name=""
@app.route("/uploader/<string:sno>", methods=["POST", "GET"])
def uploader_get(sno):
    if sno.isnumeric() != True:
        return  redirect("/dashboard")
    movie = Movies.query.filter_by(sno=sno).first()
    if session['user'] == params['username'] and 'user' in session:
        if request.method == 'POST':
            global image_name
            image_name = request.form.get("img_name")
            movie.img_name = image_name #this global variable will go to /uploader
            db.session.commit()
            time.sleep(2)
            return redirect('/dashboard')
        else:
            return render_template("uploader.html", movie=movie, image_name=movie.img_name)


@app.route('/uploader', methods=['POST'])
def uploader():
    if session['user'] == params['username'] and 'user' in session:
        if request.method == 'POST':
            f = request.files['files']
            f.save(os.path.join(params['path_upload'],
                                secure_filename(image_name)))
    return redirect('/dashboard')

#deleter
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
"""Having some issue in uploading photo and the name is not saving to database either from uploader/sno"""