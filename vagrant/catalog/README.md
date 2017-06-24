# Women of the Talkies
This project is a catalog of film and movies with female writers, directors, or creators. The goal of the women in media catalog is to shed a spotlight on the work of women in entertainment and provide a space for others to provide support and encouragement in a male-dominated field.

Without logging in, anyone can browse movies and directors. Once logging in using a google account, users may add movies and directors to the database. They may also leave comments on a movie, and edit or delete those comments.

## Running
Included in this submission are:
- database_setup.py
- moviedata.py
- flask_project.py
- templates directory
- static directory

First, run the command "python database_setup.py" to set up the database on your vagrant machine. Second, run "python moviedata.py" to load sample data into the database. To start the server, run "python flask_project.py" and then navigate to localhost:5000 to interact with the application. The templates and static directory contain html files and assets, respectively, used by the server for various pages.