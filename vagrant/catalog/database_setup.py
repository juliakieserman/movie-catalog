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

	def to_json(self):
		return dict(id=self.id,
			first_name=self.first_name,
			last_name=self.last_name,
			school=self.school)

class Movie(Base):
	__tablename__ = 'movie'

	id = Column(Integer, primary_key=True)
	title = Column(String(250), nullable=False)
	poster = Column(String(250), nullable=False)
	summary = Column(String(250), nullable=False)
	release_date = Column(String(250), nullable=False)
	director_id = Column(Integer, ForeignKey('person.id'))
	director = relationship(Person)
	user_id = Column(Integer, ForeignKey('userProfile.id'))
	user = relationship(UserProfile)

	def to_json(self):
		return dict(id=self.id,
			title=self.title,
			poster=self.poster,
			summary=self.summary,
			release_date=self.release_date,
			director= self.director.to_json())

class Comment(Base):
	__tablename__ = 'comment'

	id = Column(Integer, primary_key=True)
	data = Column(String(200), nullable=False)
	user_id = Column(Integer, ForeignKey('userProfile.id'))
	user = relationship(UserProfile)
	movie_id = Column(Integer, ForeignKey('movie.id'))
	movie = relationship(Movie)

class Rating(Base):
	__tablename__ = 'rating'

	id = Column(Integer, primary_key=True)
	rating = Column(Integer, nullable=False)
	movie_id = Column(Integer, ForeignKey('movie.id'))
	movie = relationship(Movie)
	user_id = Column(Integer, ForeignKey('userProfile.id'))
	user = relationship(UserProfile)

engine = create_engine('sqlite:///moviereviews.db')

Base.metadata.create_all(engine)