from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Movie, Base

engine = create_engine('sqlite:///moviereviews.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# movie data 
manchester_by_the_sea = Movie(title="Manchester By The Sea", 
	summary="A depressed uncle is asked to take care of his teenage nephew after the boy's father dies.",
	industry_rating="R")

session.add(manchester_by_the_sea)
session.commit()

rain_man = Movie(title="Rain Man", 
	summary="Selfish yuppie Charlie Babbitt's father left a fortune to his savant brother Raymond and a pittance to Charlie; they travel cross-country.",
	industry_rating="R")

session.add(rain_man)
session.commit()

the_circle = Movie(title="The Circle",
	summary="A woman lands a dream job at a powerful tech company called the Circle, only to uncover an agenda that will affect the lives of all of humanity.",
	industry_rating="PG13")

session.add(the_circle)
session.commit()

whiplash = Movie(title="Whiplash",
	summary="A promising young drummer enrolls at a cut-throat music conservatory where his dreams of greatness are mentored by an instructor who will stop at nothing to realize a student's potential.",
	industry_rating="R")

session.add(whiplash)
session.commit()

wonder_woman = Movie(title="Wonder Woman",
	summary="Before she was Wonder Woman she was Diana, princess of the Amazons, trained warrior. When a pilot crashes and tells of conflict in the outside world, she leaves home to fight a war to end all wars, discovering her full powers and true destiny.",
	industry_rating="PG13")

session.add(wonder_woman)
session.commit()

while_you_sleeping = Movie(title="While You Were Sleeping",
	summary="A hopeless romantic Chicago Transit Authority token collector is mistaken for the fiancee of a coma patient.",
	industry_rating="PG")

session.add(while_you_sleeping)
session.commit()

print("added movie items!")