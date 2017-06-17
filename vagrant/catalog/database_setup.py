from sqlalchemy import Column, ForeignKey, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

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