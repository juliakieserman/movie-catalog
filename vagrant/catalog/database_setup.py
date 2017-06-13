import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
	__tablename__ = 'user'
	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)

class UserRating(Base):
	__tablename__ = 'rating'
	id = Column(Integer, primary_key=True)
	user = Column(Integer, ForeignKey('user.id'))
	movie = Column(Integer, ForeignKey('movie.id'))
	created = Column(DateTime, default=datetime.datetime.utcnow)

class Movie(Base):
	__tablename__ = 'movie'

	id = Column(Integer, primary_key=True)
	title = Column(String(250), nullable=False)
	poster = Column(String(250))
	summary = Column(String(250), nullable=False)
	industry_rating = Column(Enum('G', 'PG', 'PG13', 'R', 'NC', 'U', name='industry_rating_types'))

class MovieRating(Base):
	__tablename__ = 'movie_rating'
	id = Column(Integer, primary_key=True)
	movie_id = Column(Integer, ForeignKey('movie.id'))
	user_rating = Column(Integer, ForeignKey('rating.id'))

engine = create_engine('sqlite:///moviereviews.db')


Base.metadata.create_all(engine)