import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
# this connection string works for me
SQLALCHEMY_DATABASE_URI = 'postgresql:///fyyur'
# although you ask for a valid one which looks like more like ...
# SQLALCHEMY_DATABASE_URI = 'postgresql://udacitystudios@localhost:5432/example'