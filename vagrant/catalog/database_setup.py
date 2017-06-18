from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Text, DateTime
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class UserProfile(Base):
	__tablename__ = 'userProfile'

	id = Column(Integer, primary_key=True)
	email = Column(String(100), unique=True, nullable=False)
	name = Column(String(100), nullable=True)
	picture_url = Column(String(200))
	created_at = Column(DateTime, default=datetime.datetime.utcnow())

class Person(Base):
	__tablename__ = 'person'

	id = Column(Integer, primary_key=True)
	first_name = Column(String(250), nullable=False)
	last_name = Column(String(250), nullable=False)
	school = Column(String(250))

class Movie(Base):
	__tablename__ = 'movie'

	id = Column(Integer, primary_key=True)
	title = Column(String(250), nullable=False)
	poster = Column(String(250), nullable=False)
	summary = Column(String(250), nullable=False)
	release_date = Column(String(250), nullable=False)
	director_id = Column(Integer, ForeignKey('person.id'))
	director = relationship(Person)

class Rating(Base):
	__tablename__ = 'rating'

	id = Column(Integer, primary_key=True)
	rating = Column(Integer, nullable=False)
	movie_id = Column(Integer, ForeignKey('movie.id'))

engine = create_engine('sqlite:///moviereviews.db')

Base.metadata.create_all(engine)