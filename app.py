from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from time import sleep
from collections import OrderedDict
from faker import Faker
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


# fixar en LRU cache
class LRUCache:
    def __init__(self, capacity=50):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        if key not in self.cache:
            return None
        self.cache.move_to_end(key) 
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # 50 platser finns så den sista ska pop()

    def get_all(self):
        return list(self.cache.values())[::-1]  # den som visades sist ska komma först

lru_cache = LRUCache()

@app.route("/")
def home():
    return render_template("base.html")
@app.route("/work")
def work():
    page = request.args.get('page', 1, type=int)
    per_page = 20

   #hämtar från lru
    cached_persons = lru_cache.get_all()

    # Jag hade max 50 personer i cache och 20 i varje pagination
    offset = max(0, (page - 1) * per_page - len(cached_persons))
    limit = per_page - len(cached_persons)

    # 999950 personer är kvar från databasen och de kommer och följer cache lista
    remaining_persons_query = Person.query.filter(Person.id.notin_([p.id for p in cached_persons])).offset(offset).limit(limit)
    remaining_persons = remaining_persons_query.all()

    persons = cached_persons + remaining_persons

    total_records = Person.query.count()
    total_pages = (total_records + len(cached_persons) + per_page - 1) // per_page

    return render_template("work.html", persons=persons, page=page, total_pages=total_pages)




@app.route("/person/<int:id>")
def person_detail(id):

    cached_person = lru_cache.get(id)
    if cached_person:
        print("Personen fanns i cathed data")
        person = cached_person
    else:
        print("Hämtar info från databas med delay!")
        sleep(5)  # 5 sekunder sleep
        person = Person.query.get_or_404(id)
        lru_cache.put(id, person)
    
    return render_template("person_detail.html", person=person)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")


def main():
    record_count = Person.query.count()
    if record_count >= 1000000:
        print(f"Det finns {record_count} data i datasetet så INGA nya data")
        return
    
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
        
        try:
            db.session.bulk_save_objects(persons)  
            db.session.commit()
            inserted_records += batch_size
            #för att se om data läggs till in i databaset. (Hade nåt problem med det)
            print(f"100,000 more fake records have been added to the database after {default_timer() - t_start:.2f} sekunder!")
        
        except Exception as e:
            db.session.rollback()
            print(f"An error occurred: {e}")
            break

    t_end = default_timer()
    print(f"Det tog {t_end - t_start:.2f} sekunder att skapa listan!")

if __name__ == "__main__":
    print("Creating tables...")
    with app.app_context():
        db.create_all()
        main()
        print("Tables created successfully!")

    app.run(debug=True)
