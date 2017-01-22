from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Column, Integer, String
# from app import db

engine = create_engine('sqlite:///database.db', echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

from app import db

# Set your classes here.


class User(Base):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(30))

    def __init__(self, name=None, email=None, password=None):
        self.name = name
        self.email = email
        self.password = password

class Blog(Base):
    __tablename__ = 'Blog'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    content = db.Column(db.String(300), unique=True)

    def __init__(self, name=None, content=None):
        self.name = name
        self.content = content
        self.password = password


# Create tables.
Base.metadata.create_all(bind=engine)

#The population script to add the default users to the database.
def add_or_create_person(**kwargs):
    person = db.session.query(User).filter_by(**kwargs).first()
    if person:
        return (False, person)
    else:
        person = User(**kwargs)
        db.session.add(person)
        db.session.commit()
        return (True, person)

def populate():
    people = [
        {"name": "bob", "email": "bob@farming.com", "password": "chickens123"},
        {"name": "jane", "email": "jane@farming.com", "password": "wellyboots"},
        {"name": "casey", "email": "casey@barndoors.com", "password": "pinetrees"},
    ]

    new_count = 0
    existing_count = 0
    for person in people:
        new, person = add_or_create_person(**person)
        if new:
            new_count += 1
        else:
            existing_count += 1

    return "populated with " + str(new_count) + " new, " + str(existing_count) + " existing."

print populate()
