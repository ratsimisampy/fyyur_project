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

# ---------------!!!!!!--------------------
def get_dict_list_from_result(result):
  '''Converts SQLALchemy Collections Results to Dict
  * Input: sqlalchemy.util._collections.result
  * Output: Result as list
  Source: https://stackoverflow.com/questions/48232222/how-to-deal-with-sqlalchemy-util-collections-result
  Used in following Views:
    - /venues
  '''
  list_dict = []
  for i in result:
      i_dict = i._asdict()  
      list_dict.append(i_dict)
  return list_dict
  # ---------------!!!!!!--------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  # SQL statement equivalent: SELECT city, state from Venue group by (city, state) order by city, state
  venue_query = db.session.query(Venue.city,Venue.state ).\
                     group_by(Venue.city, Venue.state).order_by(Venue.city, Venue.state).all()
  
                    
  city_state = ''
  data = []

  
  for venue in venue_query:
    print(venue.city + venue.state, venue)
    #get venues having the same city-state
    # for more details: db.session.query(Venue.id,Venue.name, Show.start_time, Show.artist_id).\
    #SQL equivalent: SELECT Id, name from Venue where city = --identified city-- and Venue.state = --identifyed state--
    venues_in_current_cityState = db.session.query(Venue.id, Venue.name).\
                                          filter(Venue.city == venue.city,
                                                    Venue.state == venue.state).all()                                                      
    
    listOf_venues_in_current_cityState = get_dict_list_from_result(venues_in_current_cityState)                                                      

    #print(listOf_venues_in_current_cityState[0]['name'])                                         
    print('venues: {} '.format(venues_in_current_cityState))
    #SQL equivalent: SELECT count(Venue.name) from Venue 
    #                                     INNER JOIN Show on Show.Id = Venue.Id
    #                                     where city = --current identifyed city-- 
    #                                             and state = --current identifyed state--
    #                                             and Show.start_time > current_time
    upcoming_shows = db.session.query(db.func.count(Venue.name)).\
                                          filter(Venue.city == venue.city,
                                                    Venue.state == venue.state).\
                                                      join(Venue.shows).\
                                                        filter(Show.start_time > current_time).\
                                                          all()                                       
    print('upcoming_shows: {} '.format(upcoming_shows))
    #the 1st time, this if condition will be skipped because city_state == ''
    if city_state == venue.city + venue.state: 
      # ignore city and state, take venues details only
      if listOf_venues_in_current_cityState:
        i = 0
        for l in listOf_venues_in_current_cityState:          
          data[len(data) - 1]["venues"].append({
            "id": listOf_venues_in_current_cityState[i]['id'],
            "name": listOf_venues_in_current_cityState[i]['name'],
            "num_upcoming_show": upcoming_shows
          })
          i = i + 1
    else:
      city_state = venue.city + venue.state
      if listOf_venues_in_current_cityState:
        i = 0
        locations = []
        for l in listOf_venues_in_current_cityState: 
          locations.append({                     
            "id": listOf_venues_in_current_cityState[i]['id'],
            "name": listOf_venues_in_current_cityState[i]['name'],
            "num_upcoming_shows": upcoming_shows            
          })
          i = i + 1
        data.append({
            "city": venue.city,
            "state": venue.state,
            "venues": locations
        })
    
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO done: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  data = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
  count = []
  for result in data:
    count.append({
      "id":result.id,
      "name": result.name      
    })
  response = {
    "count":len(data),
    "data": count
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO done: ... using JOIN query 
  
  #SQL statement equivalent: SELECT * from Venue WHERE id = venue_id
  selected_venue = Venue.query.get(venue_id)
  past_shows = []
  upcoming_shows = []

  #SQL statement equivalent: SELECT Show.* from Show INNER JOIN Venue ON Show.Id = Venue.Id
  #                                             INNER JOIN Artist ON Show.Id = Artist.Id 
  #                                             WHERE Venue.Id == venue_id       
  shows = db.session.query(Show).\
                        join(Venue).\
                          filter(Venue.id == venue_id).\
                          join(Artist)


  for show in shows:
    
    if show.start_time < str(datetime.now()):

      past_shows.append({
     "artist_id": show.artist_id,
     "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
     "artist_image_link":Venue.query.filter_by(id=show.venue_id).first().image_link ,
     "start_time": str(show.start_time) })
      print('past shows: {}'.format(past_shows))
    else:

      upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
      "artist_image_link":Venue.query.filter_by(id=show.venue_id).first().image_link ,
      "start_time": show.start_time })
      print('upcoming shows: {} '.format(upcoming_shows))
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

#  Create Artist
#  ----------------------------------------------------------------

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
    
    try:
      # Create a new instance of Venue with data from VenueForm      
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
            
      db.session.add(newVenue)      
      db.session.commit()      
      # on successful db insert, flash success
      flashType = 'success'
      flash('Venue {} was successfully listed!'.format(newVenue.name))
    except:
    # TODO DONE: on unsuccessful db insert, flash an error instead.      
      flash('An error occurred due to database insertion error. Venue {} could not be listed.'.format(form['name']))
    finally:
    # Always close session
      db.session.close()
  else:
    flash(form.errors) # Flashes reason, why form is unsuccessful (not really pretty)
    flash('An error occurred due to form validation. Venue {} could not be listed.'.format(form['name']))
    db.session.rollback()
  return render_template('pages/home.html', flashType = flashType)

#  Update venue
#  ----------------------------------------------------------------
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



@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO done: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE done: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:                              
        selected_venue = Venue.query.filter_by(id=venue_id).first_or_404()         
        db.session.delete(selected_venue)        
        db.session.commit()
        flashType = 'success'
        flash("Venue {} has been successfully deleted".format(selected_venue.name))
  except SQLAlchemyError as e:
        db.session.rollback()
        print('error: ', e)
        flashType = 'danger'
        flashType('Failed to delete venue')
  finally:
        db.session.close()
        print("hello finally")
  
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO done: replace with real data returned from querying the database
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
  

  search_term = request.form.get('search_term', '')
  data = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
  count = []
  for result in data:
    count.append({
      "id":result.id,
      "name": result.name      
    })
  response = {
    "count":len(data),
    "data": count
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO done: using JOIN query

  #SQL statement equivalent: SELECT * from Artist where Artist.Id = artist_id
  selected_artist = Artist.query.get(artist_id)
  past_shows = []
  upcoming_shows = []
  
  #SQL statement equivalent: SELECT Show.* from Show
  #                                           INNER JOIN Venue ON Show.Id = Venue.Id
  #                                           INNER JOIN Show.Id = Artist.Id 
  #                                           WHERE Artist.Id = artist_id
  #                                             
  shows = Show.query.filter_by(artist_id = artist_id).join(Artist).join(Venue)                                
                          
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
  print(data)

  return render_template('pages/show_artist.html', artist=data)

#  Update artist
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
  # TODO done: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()

  try:
    flash('hello try...{}'.format(form.phone))
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

    flash('edited_artist')
  
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
    
    try:
      # Create a new instance of Venue with data from VenueForm
    
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
            
      db.session.add(newArtist)      
      db.session.commit()      
      # on successful db insert, flash success
      flashType = 'success'
      flash('Artist {} was successfully listed!'.format(newArtist.name))
    except SQLAlchemyError as e:
      print(e)
    # TODO DONE: on unsuccessful db insert, flash an error instead.      
      flash('An error occurred due to database insertion error. Artist {} could not be listed.'.format(form['name']))
      db.session.rollback()
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
  shows = db.session.query(Show).\
                        join(Venue).\
                          join(Artist)
  
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
      db.session.rollback()
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
