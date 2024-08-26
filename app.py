from flask import Flask, render_template
from faker import Faker
from flask_sqlalchemy import SQLAlchemy
from timeit import default_timer

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:golestan5@localhost:3307/inl1'
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


def main():
    record_count = Person.query.count()
    if record_count > 0:
        print(f"Det finns {record_count} data i datasetet så INGA nya data")
        return
    

    t_start = default_timer()
    total_records = 1000000
    persons = []

    for _ in range(total_records):
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
        if _ % 100000 == 0:  
            t_end_jämn = default_timer()
            print(f"{_} records created after {t_end_jämn - t_start :.2f} sekunder")
    try:
        db.session.bulk_save_objects(persons)  
        db.session.commit()
        print("1,000,000 fake records have been added to the database!")
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")

    t_end = default_timer()
    print(f"Det tog {t_end - t_start:.2f} sekunder att skapa listan!")


if __name__ == "__main__":
    with app.app_context():
        print("Creating tables...")
        db.create_all() 
        print("Tables created successfully!")
        main() 
    app.run(debug=True)
