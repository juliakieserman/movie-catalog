from flask import Flask, render_template, request
app = Flask(__name__)

#from sqlalchemy import create_engine
#from sqlalchemy.orm import sessionmaker
# import names of database tables -- from database_setup import Base, Restaurant, MenuItem
#DBSession = sessionmaker(bind=engine)
#session = DBSession()

@app.route('/')
@app.route('/home')
def homePage():
	return render_template('home.html')

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
