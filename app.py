#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate
from models import db_setup, Venue, Show, Artist
from config import SQLALCHEMY_DATABASE_URI # Import local database URI from Config File
from sqlalchemy.exc import SQLAlchemyError
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = db_setup(app)

# TODO: connect to a local postgresql database
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  
  data=[]
  venues = Venue.query.all()
  
  for venue in venues:

    
    data.append({
      "city" : venue.city ,
      "state" : venue.state ,
      "venues" : [{
        "id" : venue.id,
        "name" : venue.name 
      }]
    })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  selected_venue = Venue.query.get(venue_id)
  past_shows = []
  upcoming_shows = []
  shows = Show.query.filter_by(venue_id = venue_id).all()

  for show in shows:
    
    if show.start_time < str(datetime.now()):

      past_shows.append({
     "artist_id": show.artist_id,
     "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
     "artist_image_link":Venue.query.filter_by(id=show.venue_id).first().image_link ,
     "start_time": str(show.start_time) })

    else:

      upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
      "artist_image_link":Venue.query.filter_by(id=show.venue_id).first().image_link ,
      "start_time": show.start_time })

  data = {
    "id": selected_venue.id,
    "name": selected_venue.name,
    "genres": selected_venue.genres ,
    "address": selected_venue.address,
    "city": selected_venue.city,
    "state": selected_venue.state,
    "phone": selected_venue.phone,
    "website": selected_venue.website,
    "facebook_link": selected_venue.facebook_link,
    "seeking_talent": True,
    "seeking_description": selected_venue.description,
    "image_link":selected_venue.image_link ,
    "past_shows":past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  
  return render_template('pages/show_venue.html', venue=data)


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm() # Initialize form instance with values from the request
  flashType = 'danger' # Initialize flashType to danger. Either it will be changed to "success" on successfully db insert, or in all other cases it should be equal to "danger"
  if form.validate():
    flash("bonjour....")
    try:
      # Create a new instance of Venue with data from VenueForm
      flash('start try... {} '.format(form.name.data))
      newVenue = Venue(
        
       name = form.name.data,
       city = form.city.data,
       state = form.state.data,
       address = form.address.data,        
       phone = form.phone.data,
       image_link =form.image_link.data,
       facebook_link = form.facebook_link.data,
       description = form.description.data,
       seeking_talent = form.seeking_talent.data,
       website = form.website.data,        
       genres = form.genres.data
        
        )
      
      flash('init objet...' )
      db.session.add(newVenue)
      flash('after session add')
      db.session.commit()
      flash('after session submit')
      # on successful db insert, flash success
      flashType = 'success'
      flash('Venue {} was successfully listed!'.format(newVenue.name))
    except:
    # TODO DONE: on unsuccessful db insert, flash an error instead.
      flash(newVenue)
      flash('An error occurred due to database insertion error. Venue {} could not be listed.'.format(form['name']))
    finally:
    # Always close session
      db.session.close()
  else:
    flash(form.errors) # Flashes reason, why form is unsuccessful (not really pretty)
    flash('An error occurred due to form validation. Venue {} could not be listed.'.format(form['name']))

  return render_template('pages/home.html', flashType = flashType)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artists = Artist.query.all()

  for artist in artists:
    data.append({
      'id': artist.id,
      'name': artist.name 
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  '''
  data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }
  data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  '''

  selected_artist = Artist.query.get(artist_id)
  past_shows = []
  upcoming_shows = []
  shows = Show.query.filter_by(artist_id = artist_id).all()

  for show in shows:

    if show.start_time < str(datetime.now()):

      past_shows.append({
     "venue_id": show.venue_id,
     "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
     "venue_image_link":Venue.query.filter_by(id=show.venue_id).first().image_link ,
     "start_time": str(show.start_time) })

    else:

      upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
      "venue_image_link":Venue.query.filter_by(id=show.venue_id).first().image_link ,
      "start_time": str(show.start_time) })
  
  data={
    "id": selected_artist.id,
    "name": selected_artist.name,
    "genres": selected_artist.genres,
    "city": selected_artist.city,
    "state": selected_artist.state,
    "phone": selected_artist.phone,
    "website": selected_artist.website,
    "facebook_link": selected_artist.facebook_link,
    "seeking_venue": True,
    "seeking_description": selected_artist.seeking_description,
    "image_link": selected_artist.image_link,
    "past_shows":past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  selected_artist = Artist.query.get(artist_id)

  form.name.data = selected_artist.name
  form.genres.data = selected_artist.genres
  form.city.data = selected_artist.city  
  form.state.data = selected_artist.state
  form.phone.data = selected_artist.phone
  form.facebook_link.data = selected_artist.facebook_link
  form.seeking_venue.data = True
  form.seeking_description.data = selected_artist.seeking_description
  form.image_link.data = "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"

  print(selected_artist.genres)  

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=selected_artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()

  try:
    
    edited_artist = Artist.query.get(artist_id)
    edited_artist.name = form.name.data
    edited_artist.genres = form.genres.data
    edited_artist.city = form.city.data
    edited_artist.state = form.state.data
    edited_artist.phone = form.phone.data
    edited_artist.facebook_link = form.facebook_link.data
    edited_artist.image_link = form.image_link.data
    edit_artist.seeking_description = form.seeking_description.data
    edit_artist.seeking_venue = form.seeking_venue.data


  
    db.session.add(edited_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully edited!')
  except SQLAlchemyError as e:
    print(e)
    db.session.rollback()
    flash('An error occured when editing artist.')
  finally:
    db.session.close()


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  selected_venue = Venue.query.get(venue_id)

  form.name.data = selected_venue.name
  form.genres.data = selected_venue.genres
  form.city.data = selected_venue.city
  form.address.data = selected_venue.address
  form.state.data = selected_venue.state
  form.phone.data = selected_venue.phone
  form.facebook_link.data = selected_venue.facebook_link  

  print(form.genres.data)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=selected_venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  try:
    
    edited_venue = Venue.query.get(venue_id)
    edited_venue.name = form.name.data
    edited_venue.genres = form.genres.data
    edited_venue.city = form.city.data
    edited_venue.state = form.state.data
    edited_venue.phone = form.phone.data
    edited_venue.facebook_link = form.facebook_link.data
    edited_venue.image_link = form.image_link.data
  
    db.session.add(edited_venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully edited!')
  except SQLAlchemyError as e:
    print(e)
    db.session.rollback()
    flash('An error occured when editing venue.')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  form = ArtistForm() # Initialize form instance with values from the request
  flashType = 'danger' # Initialize flashType to danger. Either it will be changed to "success" on successfully db insert, or in all other cases it should be equal to "danger"
  if form.validate():
    flash("bonjour....")
    try:
      # Create a new instance of Venue with data from VenueForm
      flash('start try... {} '.format(form.name.data))
      newArtist = Artist(
        
       name = form.name.data,
       city = form.city.data,
       state = form.state.data,       
       phone = form.phone.data,
       image_link =form.image_link.data,
       facebook_link = form.facebook_link.data,                      
       genres = form.genres.data,
       website = form.website.data        
        )
      
      flash('init objet...' )
      db.session.add(newArtist)
      flash('after session add')
      db.session.commit()
      flash('after session submit')
      # on successful db insert, flash success
      flashType = 'success'
      flash('Artist {} was successfully listed!'.format(newArtist.name))
    except SQLAlchemyError as e:
      print(e)
    # TODO DONE: on unsuccessful db insert, flash an error instead.
      
      flash('An error occurred due to database insertion error. Artist {} could not be listed.'.format(form['name']))
    finally:
    # Always close session
      db.session.close()
  else:
    flash(form.errors) # Flashes reason, why form is unsuccessful (not really pretty)
    flash('An error occurred due to form validation.')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  data=[]
  shows = Show.query.all()
  
  for show in shows:

    
    data.append({
      "venue_id" : show.venue_id ,
      "venue_name" : Venue.query.filter_by(id = show.venue_id).first().name ,
      "artist_id" :show.artist_id,
      "artist_name" : Artist.query.filter_by(id = show.artist_id).first().name,
      "artist_image_link" : Artist.query.filter_by(id = show.artist_id).first().image_link,
      "start_time" : show.start_time
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm()
  flashType = 'danger' # Initialize flashType to danger. Either it will be changed to "success" on successfully db insert, or in all other cases it should be equal to "danger"
  if form.validate():
    flash("bonjour ....")
    try:
      # Create a new instance of Venue with data from VenueForm
      flash('start try... ')
      newShow = Show(
        venue_id = form.venue_id.data,
        artist_id = form.artist_id.data,
        start_time = form.start_time.data
      )
      db.session.add(newShow)
      db.session.commit()
  # on successful db insert, flash success
      flashType = 'success'
      flash('Show {} was successfully listed!'.format(newShow.start_time))
    except:
      flash('An error occurred due to database insertion error. Show could not be listed.')
    finally:
    # Always close session
      db.session.close()
  else:
    flash(form.errors) # Flashes reason, why form is unsuccessful (not really pretty)
    flash('An error occurred due to form validation.')

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
