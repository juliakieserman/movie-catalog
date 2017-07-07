from flask import Flask, render_template, request
from flask import make_response, url_for, redirect, jsonify
from flask_bootstrap import Bootstrap
from flask_restless import APIManager
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Movie, Person, UserProfile, Comment
from flask import session as login_session
import random
import string
import pickle

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

engine = create_engine('sqlite:///moviereviews.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__, static_url_path='/static')
apimanager = APIManager(app, session=session)
apimanager.create_api(Movie, collection_name='movie')

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"


@app.route('/')
@app.route('/home')
def homePage():
    if login_session.get('username') is True:
        if session.query(UserProfile).filter(UserProfile.email ==
                                             login_session['email']) is False:
            newUser = UserProfile(email=login_session['email'],
                                  name=login_session['username'],
                                  picture_url=login_session['picture'])
            session.add(newUser)
            session.commit()
    return render_template('home.html')


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    login_session['access_token'] = access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
        	                     ('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    return output


@app.route('/gdisconnect')
def gdisconnect():
    credentials = login_session.get('credentials')
    access_token = login_session['access_token']
    if access_token is None:
        response = make_response(json.dumps
                                 ('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    base_url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'
    url = base_url % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result.status == 200:
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps
                                 ('Failed to revoke token for given user.'),
                                 400)
        response.headers['Content-Type'] = 'application/json'
        return response

    return redirect('/login')


@app.route('/user')
def showUser():
    if 'username' not in login_session:
        return redirect('/login')
    user = session.query(UserProfile).filter_by(
        email=login_session['email']).one()
    comments = session.query(Comment).filter_by(user_id=user.id).all()
    movies = session.query(Movie).filter_by(user_id=user.id).all()
    return render_template(
        'profile.html',
        user=user, comments=comments, movies=movies)


# route to delete my comment
@app.route('/user/comment/delete/<int:id>', methods=['POST'])
def deleteComment(id):
    # make sure user is logged in
    if 'username' not in login_session:
        return redirect('/login')
    comment = session.query(Comment).filter_by(id=id).one()
    user = session.query(UserProfile).filter_by(id=comment.user_id).one()
    # make sure comment belongs to user
    if login_session['email'] != user.email:
        return redirect('/home')
    else:
        session.delete(comment)
        session.commit()
        return redirect('/user')


# route to display edit comment page
@app.route('/user/comment/edit/<int:id>', methods=['POST'])
def editComment(id):
    # make sure user is logged in
    if 'username' not in login_session:
        return redirect('/login')
    comment = session.query(Comment).filter_by(id=id).one()
    user = session.query(UserProfile).filter_by(id=comment.user_id).one()
    # make sure comment belongs to user
    if login_session['email'] != user.email:
        return redirect('/home')
    else:
        comment = session.query(Comment).filter_by(id=id).one()
        return render_template(
            'editComment.html',
            comment=comment, movie=comment.movie)


@app.route('/user/comment/edit/<int:id>/save', methods=['POST'])
def saveCommentChanges(id):
    # make sure user is logged in
    if 'username' not in login_session:
        return redirect('/login')
    comment = session.query(Comment).filter_by(id=id).one()
    user = session.query(UserProfile).filter_by(id=comment.user_id).one()
    # make sure comment belongs to user
    if login_session['email'] != user.email:
        return redirect('/home')
    else:
        changes = request.form['comment']
        comment.data = changes
        session.commit()
        return redirect('/user')


# route for viewing all directors
@app.route('/directors')
def viewDirectors():
    directors = session.query(Person).order_by(asc(Person.last_name))
    count = directors.count()
    movieMatching = {}
    # get list of movies for each director
    for d in directors:
        movies = session.query(Movie).filter_by(director_id=d.id).all()
        movieList = []
        for m in movies:
            movieVal = (m.title, m.release_date, m.id)
            movieList.append(movieVal)
        movieMatching[d.id] = movieList
    return render_template(
        'directors.html',
        directors=directors, movies=movieMatching, count=count)


# API endpoint for directors
@app.route('/directors/JSON')
def directorsJSON():
    directors = session.query(Person).order_by(asc(Person.last_name))
    return jsonify(Directors=[i.to_json() for i in directors])


# route for viewing single movie
@app.route('/movies/<int:movie_id>/', methods=['GET', 'POST'])
def showMovie(movie_id):
    movie = session.query(Movie).filter_by(id=movie_id).one()
    director = session.query(Person).filter_by(id=movie.director_id)
    comments = session.query(Comment).filter_by(movie_id=movie.id).all()

    if request.method == 'POST':
        if 'username' not in login_session:
            return redirect('/login')
        else:
            comment = request.form['comment']
            user = session.query(UserProfile).filter_by(
                email=login_session['email']).one()
            newComment = Comment(data=comment, movie=movie, user_id=user.id)
            session.add(newComment)
            session.commit()

    return render_template(
        'movie.html',
        movie=movie, director=director, comments=comments)


# API endpoint for comments
@app.route('/movies/<int:movie_id>/comments/JSON')
def commentsJSON(movie_id):
    comments = session.query(Comment).filter_by(movie_id=movie_id).all()
    return jsonify(Comment=[i.to_json() for i in comments])


# API endpoint for single movie
@app.route('/movies/<int:movie_id>/JSON')
def movieJSON(movie_id):
    movie = session.query(Movie).filter_by(id=movie_id).one()
    return jsonify(Movie=movie.to_json())


# route for viewing all movies
@app.route('/movies')
def viewMovies():
    movies = session.query(Movie).order_by(asc(Movie.title))
    return render_template('movies.html', movies=movies)


# API endpoint for all movies
@app.route('/movies/JSON')
def moviesJSON():
    movies = session.query(Movie).order_by(asc(Movie.title))
    return jsonify(Movies=[i.to_json() for i in movies])


# route for adding a new movie
@app.route('/movies/add', methods=['GET', 'POST'])
def newMovie():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'GET':
        return render_template('newMovie.html')
    else:
        lName = request.form['last_name']
        fName = request.form['first_name']
        school = request.form['school']
        title = request.form['title']
        # create person object first, if it doesn't already exist
        # NOTE: assuming no two people have the same name
        newPerson = session.query(Person).filter(
            Person.first_name == fName).filter(Person.last_name == lName)
        if newPerson is True:
            newPerson = session.query(Person).filter_by(
                first_name=fName, last_name=lName)
        else:
            newPerson = Person(first_name=fName,
                               last_name=lName, school=school)
            session.add(newPerson)
            session.commit()

        user = session.query(UserProfile).filter_by(
            email=login_session['email']).one()
        createMovieObj(title, newPerson)

    return redirect('/movies')


def createMovieObj(movie, moviePerson):
    data_string = ("https://api.themoviedb.org/3/search/movie?api_key"
                   "=0bf21ff60196bf22bce9136c1db1da7c&query=")

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

    # check to see if this movie exists
    movie = session.query(Movie).filter(Movie.poster == poster)
    if movie is False:
        newMovie = Movie(title=title, summary=summary, poster=poster,
                         release_date=release_date, director=moviePerson)

        session.add(newMovie)
        session.commit()


# handle unfound page errors
@app.errorhandler(404)
def pageNotFound(error):
    return render_template('404.html')

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
