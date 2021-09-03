from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import json
app = Flask(__name__)
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
    date =  db.Column(db.String(20), nullable=False)
# slug =  db.Column(db.String(20), nullable=False)
@app.route("/")
def home():
    movies = Movies.query.all()
    latest = Movies.query.order_by(Movies.date.desc()).limit(7).all()
    comedy = Movies.query.filter_by(genre='comedy').order_by(Movies.date.desc()).all()
    horror = Movies.query.filter_by(genre='horror').order_by(Movies.date.desc()).all()
    action = Movies.query.filter_by(genre='action').order_by(Movies.date.desc()).all()
    romance = Movies.query.filter_by(genre='romance').order_by(Movies.date.desc()).all()
    return render_template("index.html", movies=movies,latest=latest, comedy=comedy,horror=horror, action=action,romance=romance)
@app.route("/<string:slug>")
def movie_download(slug):
    movie = Movies.query.filter_by(slug=slug).first()
    return render_template("test.html", movie=movie)
@app.route("/movies")
def movies_vertical():
    # movies = Movies.query.all()
    # latest = Movies.query.order_by(Movies.date.desc()).limit(7).all()
    return render_template("movies_vertical.html")
app.run(debug=True)