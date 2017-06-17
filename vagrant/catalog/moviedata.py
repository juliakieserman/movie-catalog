from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Movie, Person, Base
import requests

# movie db api access - to get date for movie objects
data_string = ("https://api.themoviedb.org/3/search/movie?api_key"
               "=0bf21ff60196bf22bce9136c1db1da7c&query=")

engine = create_engine('sqlite:///moviereviews.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def create_person_obj(fName, lName, school):
	newPerson = Person(first_name=fName, last_name=lName, school=school)
	session.add(newPerson)
	session.commit()
	return newPerson

def create_movie_obj(movie, moviePerson):
	# collect initial data from movie database
	search_params = ''
	for word in movie.split():
		search_params += word+'+'
	search_movie = data_string + search_params

	r = requests.get(search_movie)
	response = r.json()['results'][0]
	title = response['original_title']
	summary = response['overview']
	poster = 'http://image.tmdb.org/t/p/w185/' + response['poster_path']
	release_date = response['release_date']

	newMovie = Movie(title=title, summary=summary, poster=poster, 
		release_date=release_date, director=moviePerson)

	session.add(newMovie)
	session.commit()

if __name__ == '__main__':
	moviePerson = create_person_obj("Sharon", "Maguire", "University of Wales Aberystwyth")
	create_movie_obj("Bridget Jones's Diary", moviePerson)

	moviePerson = create_person_obj("Susan", "Seidelman", "New York University")
	create_movie_obj("Desperately Seeking Susan", moviePerson)

	moviePerson = create_person_obj("Kathryn", "Bigelow", "Columbia University")
	create_movie_obj("The Hurt Locker", moviePerson)
	
	moviePerson = create_person_obj("Jocelyn", "Moorhouse", "Australian Film, Television and Radio School (AFTRS)")
	create_movie_obj("Proof", moviePerson)

	moviePerson = create_person_obj("Barbra", "Streisand", "Erasmus Hall High School")
	create_movie_obj("The Prince of Tides", moviePerson)

	moviePerson = create_person_obj("Julie", "Taymor", "Oberlin College")
	create_movie_obj("Frida", moviePerson)

	moviePerson = create_person_obj("Clio", "Barnard", "Northumbria University")
	create_movie_obj("The Arbor", moviePerson)

	moviePerson = create_person_obj("Gurinder", "Chadha", "University of East Anglia")
	create_movie_obj("Bend It Like Beckham", moviePerson)

	moviePerson = create_person_obj("Sarah", "Gavron", "Edinburgh College of Art")
	create_movie_obj("Suffragette", moviePerson)

	#Movie.__table__.drop()
