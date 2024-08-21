from flask import Flask, render_template
from faker import Faker
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:golestan5@localhost/inl1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

faker = Faker('sv_SE')

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    namn = db.Column(db.String(100), nullable=False)
    efternamn = db.Column(db.String(100), nullable=False)
    personnummer = db.Column(db.String(12), unique=True, nullable=False)
    stad = db.Column(db.String(100), nullable=False)
    land = db.Column(db.String(100), nullable=False)
    yrke = db.Column(db.String(100), nullable=False)
    telefonnummer = db.Column(db.String(11), nullable=False)

    def __repr__(self):
        return f"<Person {self.namn} {self.efternamn}>"

@app.route("/")
def home():
    return render_template("base.html")

if __name__ == "__main__":
    app.run(debug=True)