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
    return render_template("index.html", movies=movies)
@app.route("/<string:slug>")
def movie_download(slug):
    movie = Movies.query.filter_by(slug=slug).first()
    return render_template("test.html", movie=movie)

app.run(debug=True)