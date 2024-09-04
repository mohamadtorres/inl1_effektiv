from flask import Flask, render_template,request
from faker import Faker
from flask_sqlalchemy import SQLAlchemy
from timeit import default_timer
import os

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


@app.route("/work")
def work():
    page = request.args.get('page', 1, type=int)
    persons = Person.query.paginate(page=page, per_page=20)
    print(f"Total persons: {persons.total}")  # This should print 1000000
    print(f"Items on this page: {len(persons.items)}")  # This should print the number of items on the current page
    return render_template("work.html", persons=persons)

@app.route("/person/<int:id>")
def person_detail(id):
    person = Person.query.get_or_404(id)
    return render_template("person_detail.html", person=person)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")


def main():
    record_count = Person.query.count()
    if record_count > 1000000:
        print(f"Det finns {record_count} data i datasetet så INGA nya data")
        return
    

    # t_start = default_timer()
    # total_records = 1000000
    # persons = []

    # for _ in range(total_records):
    #     person = Person(
    #         namn=faker.first_name(),
    #         efternamn=faker.last_name(),
    #         personnummer=faker.unique.ssn(),
    #         stad=faker.city(),
    #         land=faker.country(),
    #         yrke=faker.job(),
    #         telefonnummer=faker.phone_number()
    #     )

    t_start = default_timer()
    total_records = 1000000
    batch_size = 100000
    inserted_records = record_count

    while inserted_records < total_records:
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
        
        # if _ % 100000 == 0:  
        #     print(f"{_} records created after {default_timer() - t_start :.2f} sekunder")
        try:
            db.session.bulk_save_objects(persons)  
            db.session.commit()
            inserted_records += batch_size
            print(f"100,000 more fake records have been added to the database after {default_timer() - t_start:.2f} sekunder!")
        
        except Exception as e:
            db.session.rollback()
            print(f"An error occurred: {e}")
            break


    t_end = default_timer()
    print(f"Det tog {t_end - t_start:.2f} sekunder att skapa listan!")

if __name__ == "__main__":
    if not app.debug:
        print("Creating tables...")
        with app.app_context():
            db.create_all()
            main()
            print("Tables created successfully!")


    app.run(debug=True)


