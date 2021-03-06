from flask import Flask, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import json
import datetime
from flask_wtf.csrf import CSRFProtect
import time
import os
import math
from flask_msearch import Search
app = Flask(__name__)
app.secret_key = 'super secret key'
csrf = CSRFProtect(app)
params = json.load(open('config.json'))['params']
# print(params)
app.config['SQLALCHEMY_DATABASE_URI'] = params['data_base_uri']
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
search = Search(db=db)
search.init_app(app)


def pagination(movies):
    """It will return the pagination movie number in any page that I want"""
    page = request.args.get('page')
    last = math.ceil(len(movies)/int(params['no_of_movies']))
    # print(last)
    # print(page)
    display_priv = '#'
    display_next = '#'
    justify_content = "justify-content-between"
    if str(page).isnumeric() != True:
        page = 1
    elif int(page) > last:
        page = last
    elif int(page) < 1:
        page = 1
    if int(page) == 1:
        priv = '#'
        next = int(page) + 1
        display_priv = "display:none;"
        justify_content = "justify-content-end"
    elif int(page) == last:
        next = '#'
        display_next = "display:none;"
        priv = int(page) - 1
    else:
        priv = int(page) - 1
        next = int(page) + 1
    movies = movies[(int(page)-1) * params['no_of_movies']:int(page)*params['no_of_movies']]
    return {"movies": movies, "display_next": display_next, "display_priv": display_priv, "priv": priv, "next": next, "justify_content": justify_content, "page": page}


class Movies(db.Model):
    __tablename__ = 'movies'
    __searchable__ = ['name', 'description', 'cast']
    sno = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    slug = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(200), nullable=False)
    director = db.Column(db.String(200), nullable=False)
    cast = db.Column(db.String(200), nullable=False)
    lang = db.Column(db.String(200), nullable=False)
    img_name = db.Column(db.String(20), nullable=False)
    film_industry = db.Column(db.String(20), nullable=False)
    # mega_link = db.Column(db.String(20), nullable=False)
    youtube_link = db.Column(db.String(20), nullable=False)
    # gdrive_link = db.Column(db.String(20), nullable=False)
    meta_description = db.Column(db.String(20), nullable=True)
    meta_keywords = db.Column(db.String(20), nullable=True)
    date = db.Column(db.String(20), nullable=False)
# slug =  db.Column(db.String(20), nullable=False)


class Highlinks(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    mega_link = db.Column(db.String(20), nullable=True)
    gdrive_link = db.Column(db.String(20), nullable=True)
    onedrive_link = db.Column(db.String(200), nullable=True)
    mirror_link = db.Column(db.String(200), nullable=True)
    name = 'highlink'
    quality = "1080p"


class Mediumlinks(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    mega_link = db.Column(db.String(20), nullable=True)
    gdrive_link = db.Column(db.String(20), nullable=True)
    onedrive_link = db.Column(db.String(200), nullable=True)
    mirror_link = db.Column(db.String(200), nullable=True)
    name = 'mediumlink'
    quality = '720p'


class Lowlinks(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    mega_link = db.Column(db.String(20), nullable=True)
    gdrive_link = db.Column(db.String(20), nullable=True)
    onedrive_link = db.Column(db.String(200), nullable=True)
    mirror_link = db.Column(db.String(200), nullable=True)
    name = 'lowlink'
    quality = '480p'


@app.route("/")
def home():
    # movies = Movies.query.all()
    latest = Movies.query.order_by(Movies.date.desc()).all()
    latest = pagination(latest)
    # Have to make catagory wise selection.
    catagory = request.args.get('catagory')
    if catagory == "film":
        "anime"
        action = Movies.query.filter_by(
            film_industry='anime').order_by(Movies.date.desc()).all()
        action = pagination(action)
        "hollywood"
        romance = Movies.query.filter_by(
            film_industry='hollywood').order_by(Movies.date.desc()).all()
        romance = pagination(romance)
        "bollywood"
        horror = Movies.query.filter_by(
            film_industry='bollywood').order_by(Movies.date.desc()).all()
        horror = pagination(horror)
        "others"
        comedy = Movies.query.filter(Movies.film_industry != 'bollywood').filter(
            Movies.film_industry != 'hollywood').filter(Movies.film_industry != 'anime').order_by(Movies.date.desc()).all()
        comedy = pagination(comedy)
        first_row, second_row, third_row, fourth_row = [
            "Anime", "Hollywood", "Bollywood", "Others"]
    else:
        action = Movies.query.filter_by(
            genre='action').order_by(Movies.date.desc()).all()
        action = pagination(action)
        romance = Movies.query.filter_by(
            genre='romance').order_by(Movies.date.desc()).all()
        romance = pagination(romance)
        horror = Movies.query.filter_by(
            genre='horror').order_by(Movies.date.desc()).all()
        horror = pagination(horror)
        comedy = Movies.query.filter_by(
            genre='comedy').order_by(Movies.date.desc()).all()
        comedy = pagination(comedy)
        first_row, second_row, third_row, fourth_row = [
            "Action", "Romance", "Horror", "Comedy"]
    return render_template("index.html", latest=latest["movies"], comedy=comedy["movies"], horror=horror["movies"], action=action["movies"], romance=romance["movies"], first_row=first_row, second_row=second_row, third_row=third_row, fourth_row=fourth_row, next=latest["next"], priv=latest['priv'], display_next=latest["display_next"], display_priv=latest["display_priv"], justify_content=latest["justify_content"])


@app.route("/movies/download/<string:slug>")
def movie_download(slug):
    movie = Movies.query.filter_by(slug=slug).first()
    highlink = Highlinks.query.filter_by(sno=movie.sno).first()
    mediumlink = Mediumlinks.query.filter_by(sno=movie.sno).first()
    lowlink = Lowlinks.query.filter_by(sno=movie.sno).first()
    return render_template("download_movies.html", movie=movie, highlink=highlink, mediumlink=mediumlink, lowlink=lowlink)


"""Vertically movies display"""


@app.route("/industry/<string:genre>")
def movies_vertical(genre):
    # movies = Movies.query.all()
    if genre.lower() == "others":
        movies = Movies.query.filter(Movies.film_industry != 'bollywood').filter(
            Movies.film_industry != 'hollywood').filter(Movies.film_industry != 'anime').order_by(Movies.date.desc()).all()
        movies = pagination(movies)
        # print(movie)
    else:
        # genre = genre.lower()
        movies = Movies.query.filter_by(genre=genre).order_by(
            Movies.date.desc()).limit(7).all()
        # movies = Movies.query.all()
        if len(movies) == 0:
            movies = Movies.query.filter_by(film_industry=genre).order_by(
                Movies.date.desc()).limit(7).all()
        movies = pagination(movies)
    return render_template("movies_vertical.html", movies=movies["movies"], display_next=movies["display_next"], display_priv=movies["display_priv"], next=movies["next"], priv=movies["priv"], justify_content=movies["justify_content"], genre=genre)
    # return render_template("movies_vertical.html", movies=movies)


"""Dash Board"""


@app.route("/dashboard", methods=['GET',  'POST'])
def dashboard():
    query = request.args.get("search")
    try:
        movies = Movies.query.msearch(
            query, fields=['name', 'description', 'cast']).order_by(Movies.date.desc()).all()
    except:
        movies = Movies.query.order_by(Movies.date.desc()).all()
    movies = pagination(movies)
    if ('user' in session and session['user'] == params['username']):
        return render_template('dashboard.html', name='Admin Panel', movies=movies["movies"], priv=movies["priv"], next=movies["next"], display_next=movies["display_next"], display_priv=movies["display_priv"], justify_content=movies["justify_content"], page=movies["page"])
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
    if session['user'] == params['username'] and 'user' in session:
        movie = Movies.query.filter_by(sno=sno).first()
        highlink = Highlinks.query.filter_by(sno=sno).first()
        lowlink = Lowlinks.query.filter_by(sno=sno).first()
        mediumlink = Mediumlinks.query.filter_by(sno=sno).first()
        if request.method == 'GET':
            if sno == '0':
                return render_template("add.html", movie=movie, sno=sno, img_name='s-1.jpg', highlink=highlink, lowlink=lowlink, mediumlink=mediumlink)
            else:
                return render_template("edit.html", movie=movie, sno=sno, img_name=movie.img_name, highlink=highlink, lowlink=lowlink, mediumlink=mediumlink)
        elif request.method == 'POST':
            name = request.form.get('name')
            slug = request.form.get('slug').replace(' ', '_').lower()
            description = request.form.get('description')
            genre = request.form.get('genre').lower()
            director = request.form.get('director').lower()
            cast = request.form.get('cast').lower()
            lang = request.form.get('lang').lower()

            film_industry = request.form.get('film_industry').lower()
            global image_name  # This global variable will go to /uploader
            image_name = request.form.get("img_name")
            youtube_link = request.form.get("youtube_link")
            # Download Links
            mega_link_1080 = request.form.get('highlink_mega_link')
            gdrive_link_1080 = request.form.get('highlink_gdrive_link')
            onedrive_link_1080 = request.form.get('highlink_onedrive_link')
            mirror_link_1080 = request.form.get('highlink_mirror_link')
            mega_link_720 = request.form.get('mediumlink_mega_link')
            gdrive_link_720 = request.form.get('mediumlink_gdrive_link')
            onedrive_link_720 = request.form.get('mediumlink_onedrive_link')
            mirror_link_720 = request.form.get('mediumlink_mirror_link')
            mega_link_480 = request.form.get('lowlink_mega_link')
            gdrive_link_480 = request.form.get('lowlink_gdrive_link')
            onedrive_link_480 = request.form.get('lowlink_onedrive_link')
            mirror_link_480 = request.form.get('lowlink_mirror_link')
            # we could use f.filename instead of img_name As we are taking input from the user for the file name I didn't save with the filename uploading I am saving with the filename the user giving
            if sno == '0':
                post = Movies(name=name, slug=slug,
                              description=description, genre=genre, director=director, cast=cast, lang=lang, film_industry=film_industry, date=datetime.datetime.now(), img_name=image_name, youtube_link=youtube_link)
                try:
                    f = request.files['files']
                    f.save(os.path.join(params['path_upload'],
                                        secure_filename(image_name)))
                except:
                    pass
                db.session.add(post)
                db.session.commit()
                sno = Movies.query.order_by(Movies.date.desc()).first().sno
                link_1080 = Highlinks(sno=sno, mega_link=mega_link_1080, gdrive_link=gdrive_link_1080,
                                      onedrive_link=onedrive_link_1080, mirror_link=mirror_link_1080)
                link_720 = Mediumlinks(sno=sno, mega_link=mega_link_720, gdrive_link=gdrive_link_720,
                                       onedrive_link=onedrive_link_720, mirror_link=mirror_link_720)
                link_480 = Lowlinks(sno=sno, mega_link=mega_link_480, gdrive_link=gdrive_link_480,
                                    onedrive_link=onedrive_link_480, mirror_link=mirror_link_480)
                db.session.add(link_1080)
                db.session.add(link_720)
                db.session.add(link_480)
                db.session.commit()
            else:
                movie = Movies.query.filter_by(sno=sno).first()
                highlink = Highlinks.query.filter_by(sno=sno).first()
                mediumlink = Mediumlinks.query.filter_by(sno=sno).first()
                lowlink = Lowlinks.query.filter_by(sno=sno).first()
                """Adding to the database"""
                movie.name = name
                movie.slug = slug
                movie.description = description
                movie.genre = genre
                movie.director = director
                movie.cast = cast
                movie.lang = lang
                movie.film_industry = film_industry
                movie.img_name = image_name
                # movie.gdrive_link = gdrive_link
                movie.youtube_link = youtube_link
                # movie.mega_link = mega_link
                highlink.mega_link = mega_link_1080
                highlink.gdrive_link = gdrive_link_1080
                highlink.onedrive_link = onedrive_link_1080
                highlink.mirror_link = mirror_link_1080
                mediumlink.mega_link = mega_link_720
                mediumlink.gdrive_link = gdrive_link_720
                mediumlink.onedrive_link = onedrive_link_720
                mediumlink.mirror_link = mirror_link_720
                lowlink.mega_link = mega_link_480
                lowlink.gdrive_link = gdrive_link_480
                lowlink.onedrive_link = onedrive_link_480
                lowlink.mirror_link = mirror_link_480
                db.session.commit()
            time.sleep(2)
            return redirect('/dashboard')
    return redirect('/dashboard')


"""SEO = Search Engine Optimization"""


@app.route("/seo/<string:sno>", methods=["GET", "POST"])
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
        return render_template("seo_edit.html", meta_description=meta_description, meta_keywords=meta_keywords, img_name=img_name, sno=sno)
    elif request.method == "POST":
        # It's adding the seo after the row is made so It is using commit(), By default it will be null in the database
        meta_description = request.form.get('meta_description')
        meta_keywords = request.form.get('meta_keywords')
        movies.meta_description = meta_description
        movies.meta_keywords = meta_keywords
        db.session.commit()
        return redirect("/dashboard")


# Image uploader
image_name = ""


@app.route("/uploader/<string:sno>", methods=["POST", "GET"])
def uploader_get(sno):
    if sno.isnumeric() != True:
        return redirect("/dashboard")
    movie = Movies.query.filter_by(sno=sno).first()
    if session['user'] == params['username'] and 'user' in session:
        if request.method == 'POST':
            global image_name
            image_name = request.form.get("img_name")
            movie.img_name = image_name  # this global variable will go to /uploader
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

# deleter


@app.route('/delete/<string:sno>')
def deleter(sno):
    if session['user'] == params['username'] and 'user' in session:
        post = Movies.query.filter_by(sno=sno).first()
        image_name = post.img_name
        try:
            os.remove(os.path.join(params['path_upload'],
                                   secure_filename(image_name)))
        except:
            pass
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")

# Searcher


@app.route('/search')
def search():
    query = request.args.get('query')
    movies = Movies.query.msearch(
        query, fields=['name', 'description', 'cast']).order_by(Movies.date.desc()).all()
    movies = pagination(movies)
    return render_template('search.html', movies=movies["movies"], display_next=movies["display_next"], display_priv=movies["display_priv"], next=movies["next"], priv=movies["priv"], justify_content=movies["justify_content"], genre=query)


if __name__ == '__main__':
    app.run(debug=True)
    """Still have to add if else in test.html have to add the meta description and title in page"""
"""Having some issue in uploading photo and the name is not saving to database either from uploader/sno"""
