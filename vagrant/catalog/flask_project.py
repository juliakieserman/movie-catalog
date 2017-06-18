from flask import Flask, render_template, request, make_response, url_for
from flask_bootstrap import Bootstrap
from flask_scss import Scss
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Movie, Rating, Person, UserProfile
from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

app = Flask(__name__, static_url_path='/static')
Scss(app, static_dir='static', asset_dir='assets')

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

engine = create_engine('sqlite:///moviereviews.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.context_processor
def if_user():
	isUser = ''
	loggedIn = False
	if 'username' in login_session is False:
		isUser = 'Log In'
	else:
		isUser = 'Log Out'
		loggedIn = True
	return dict(isUser = isUser, loggedIn = loggedIn)

@app.route('/')
@app.route('/home')
def homePage():
	if 'username' in login_session:
		q = session.query(UserProfile.id).filter(UserProfile.email == login_session['email'])
    	if session.query(q.exists()).scalar() == False:
    		newUser = UserProfile(email=login_session['email'], name=login_session['username'], picture_url=login_session['picture'])
    		session.add(newUser)
    		session.commit()
    		print('made new user!')
    		print(newUser)

	return render_template('home.html')

@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
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
        response = make_response(json.dumps('Current user is already connected.'),
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
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    print("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/gdisconnect')
def gdisconnect():
    credentials = login_session['credentials'].to_json()
    print('credentials')
    print(credentials)
    access_token = credentials.access_token
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: ' 
    print login_session['username']
    if access_token is None:
 	print 'Access Token is None'
    	response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
	del login_session['access_token'] 
    	del login_session['gplus_id']
    	del login_session['username']
    	del login_session['email']
    	del login_session['picture']
    	response = make_response(json.dumps('Successfully disconnected.'), 200)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    else:
	
    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response

@app.route('/user')
def showUser():
	if 'username' not in login_session:
		return redirect('/login')
	user = session.query(UserProfile).filter_by(email=login_session['email']).one()
	print(user.email)
	print(user.name)
	print(user.picture_url)
	return render_template('profile.html', user=user)

@app.route('/directors')
def viewDirectors():
	directors = session.query(Person).order_by(asc(Person.last_name))
	return render_template('directors.html', directors=directors)

@app.route('/movie/<int:movie_id>/')
def showMovie(movie_id):
	movie = session.query(Movie).filter_by(id=movie_id).one()
	ratings = session.query(Rating).filter_by(movie_id = movie_id)
	return render_template('movie.html', movie=movie)

@app.route('/movies')
def viewMovies():
	movies = session.query(Movie).order_by(asc(Movie.title))
	return render_template('movies.html', movies = movies)

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
		newPerson = session.query(Person).filter(Person.first_name == fName).filter(Person.last_name == lName)
		if newPerson is True:
			print('in dis loop')
			newPerson = session.query(Person).filter_by(first_name=fName, last_name=lName)
		else:
			print('this is the loop)')
			newPerson = Person(first_name=fName, last_name=lName, school=school)
			session.add(newPerson)
			session.commit()

		user = session.query(UserProfile).filter_by(email=login_session['email']).one()
		print(user)
		movieObj = createMovieObj(title, newPerson)

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

	newMovie = Movie(title=title, summary=summary, poster=poster, 
		release_date=release_date, director=moviePerson)

	session.add(newMovie)
	session.commit()
	return newMovie

@app.route('/submit_rating', methods=['POST'])
def submitRating():
	print(request.form['star5'])

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
