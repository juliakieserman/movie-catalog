#from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_scss import Scss
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Movie, Rating, Person
from flask import session as login_session
import random
import string

app = Flask(__name__, static_url_path='/static')
Scss(app, static_dir='static', asset_dir='assets')

engine = create_engine('sqlite:///moviereviews.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/home')
def homePage():
	movies = session.query(Movie).order_by(asc(Movie.title))
	return render_template('home.html', movies = movies)

@app.route('/movie/<int:movie_id>/')
def showMovie(movie_id):
	movie = session.query(Movie).filter_by(id=movie_id).one()
	ratings = session.query(Rating).filter_by(movie_id = movie_id)
	return render_template('movie.html', movie=movie)

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
