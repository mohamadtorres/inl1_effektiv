from flask import Flask, render_template
from faker import Faker
from flask_sqlalchemy import SQLAlchemy

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
    telefonnummer = db.Column(db.String(20), nullable=False) 

    def __repr__(self):
        return f"<Person {self.namn} {self.efternamn}>"

@app.route("/")
def home():
    return render_template("base.html")

@app.route("/populate")
def populate():
    batch_size = 10000  # Adjust batch size as needed
    total_records = 1000000

    for _ in range(0, total_records, batch_size):
        persons = []
        for _ in range(batch_size):
            person = Person(
                namn=faker.first_name(),
                efternamn=faker.last_name(),
                personnummer=faker.unique.ssn(),
                stad=faker.city(),
                land=faker.country(),
                yrke=faker.job(),
                telefonnummer=faker.phone_number()
            )
            persons.append(person)

        try:
            db.session.bulk_save_objects(persons)  
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return f"An error occurred: {e}"

    return "1,000,000 fake records have been added to the database!"

if __name__ == "__main__":
    db.create_all() 
    app.run(debug=True)
