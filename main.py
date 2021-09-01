from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import json
app = Flask(__name__)
params = json.load(open('config.json'))['params']
print(params)
app.config['SQLALCHEMY_DATABASE_URI'] = params['data_base_uri'] 
db = SQLAlchemy(app)
class movies(db.Model): 
    sno = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(20), nullable=False) 
    description = db.Column(db.String(200), nullable=False)
    slug =  db.Column(db.String(20), nullable=False)
    img_name =  db.Column(db.String(20), nullable=False)
    datatime =  db.Column(db.String(20), nullable=False)
# slug =  db.Column(db.String(20), nullable=False)
@app.route("/")
def hello_world():
    return render_template("index.html")

app.run(debug=True)