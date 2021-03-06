# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import (Flask, render_template, request,
                   Response, flash, redirect, url_for)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String()))
    website = db.Column(db.String(500), nullable=True)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue',
                            lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<VENUE [ ID :{self.id}  NAME :{self.name} ] >'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))

    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    website = db.Column(db.String(500), nullable=True)
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist ID: {self.id}, name: {self.name}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),
                          nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'),
                         nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.today())

    def __repr__(self):
        return f'<SHOW  [id: {self.id} \n venue_id: {self.venue_id} \n artist_id: {self.artist_id} \n start_time: {self.start_time}]>'


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    def count_future_shows(shows):
        x = 0
        for show in shows:
            if show.start_time > datetime.now():
                x += 1
        return x
    data = []
    venues_cities = Venue.query.distinct(Venue.city).all()

    for d_venue in venues_cities:
        city = d_venue.city
        venues = Venue.query.filter_by(city=city).all()
        state = venues[0].state
        data.append({
            "city": city,
            "state": state,
            "venues": [{"id": venue.id,
                        "name": venue.name,
                        "num_upcoming_shows": count_future_shows(venue.shows)} for venue in venues]
        })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    term = request.form.get('search_term', '')
    matched_venues = Venue.query.filter(Venue.name.ilike('%' + term + '%'))
    data = []
    for venue in matched_venues:
        data.append({'id': venue.id, 'name': venue.name})

    response = {'count': matched_venues.count(), 'data': data}
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    past_shows = []
    upcoming_shows = []
    for show in venue.shows:
        artist = Artist.query.get(show.artist_id)
        show_data = {
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time)
        }
        if show.start_time > datetime.now():
            upcoming_shows.append(show_data)
        else:
            past_shows.append(show_data)
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    form = VenueForm()
    # CHECK IF VALID. IF NOT KEEP USER ON PAGE TO MAKE CORRECTIONS
    if form.validate_on_submit():
        try:
            new_venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                genres=form.genres.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data,
                image_link=form.image_link.data,
                website=form.website.data,
                facebook_link=form.facebook_link.data,
            )

            db.session.add(new_venue)
            db.session.commit()
        except:
            error = True
            print(sys.exc_info())
            db.session.rollback()
        finally:
            db.session.close()
            if error:
                flash(
                    'An error occurred. Venue '
                    + request.form['name']
                    + ' could not be listed.'
                )
            else:
                flash(
                    'Venue ' + request.form['name'] + ' was successfully listed!')
    else:
        flash('Please! fill all fields with the correct format')

        flash(form.errors)

        return render_template('forms/new_venue.html', form=form)

    return redirect(url_for('index'))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    venue = Venue.query.get(venue_id)
    venue_name = venue.name
    try:
        db.session.delete(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if error:
        flash('An Error Occured')
    else:
        flash('Venue ' + venue_name + ' was successfully deleted!')
    return redirect(url_for('index'))
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database

    artists = Artist.query.all()
    data = [{
        "id": artist.id,
        "name": artist.name,
    } for artist in artists]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    term = request.form.get('search_term', '')
    matched_artists = Artist.query.filter(Artist.name.ilike('%' + term + '%'))
    data = []
    for artist in matched_artists:
        data.append({'id': artist.id, 'name': artist.name})

    response = {'count': matched_artists.count(), 'data': data}
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    artist = Artist.query.get(artist_id)
    past_shows = []
    upcoming_shows = []
    for show in artist.shows:
        venue = Venue.query.get(show.venue_id)
        show_data = {
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": str(show.start_time)
        }
        if show.start_time > datetime.now():
            upcoming_shows.append(show_data)
        else:
            past_shows.append(show_data)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get(artist_id)
    form = ArtistForm()
    error = False

    if form.validate_on_submit():
        try:
            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.genres = form.genres.data
            artist.seeking_venue = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data
            artist.image_link = form.image_link.data
            artist.website = form.website.data
            artist.facebook_link = form.facebook_link.data

            db.session.commit()
        except:
            error = True
            print(sys.exc_info())
            db.session.rollback()
        finally:
            db.session.close()
            if error:
                flash(
                    'An error occurred. Artist '
                    + request.form['name']
                    + ' could not be listed.'
                )
            else:
                flash('Artist ' +
                      request.form['name'] + ' was successfully listed!')
    else:
        flash('please fill the fields with the correct format')
        flash(form.errors)
        return render_template('forms/edit_artist.html', form=form, artist=artist)
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)

    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.get(venue_id)
    form = VenueForm()
    error = False

    if form.validate_on_submit():
        try:
            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.address = form.address.data
            venue.phone = form.phone.data
            venue.genres = form.genres.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data
            venue.image_link = form.image_link.data
            venue.website = form.website.data
            venue.facebook_link = form.facebook_link.data

            db.session.commit()
        except:
            error = True
            print(sys.exc_info())
            db.session.rollback()
        finally:
            db.session.close()
            if error:
                flash(
                    'An error occurred. Venue '
                    + request.form['name']
                    + ' could not be listed.'
                )
            else:
                flash(
                    'Venue ' + request.form['name'] + ' was successfully edited!')
    else:
        flash('please fill the fields with the correct format')
        flash(form.errors)
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    form = ArtistForm()

    if form.validate_on_submit():
        try:
            new_artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=form.genres.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data,
                image_link=form.image_link.data,
                website=form.website.data,
                facebook_link=form.facebook_link.data,
            )

            db.session.add(new_artist)
            db.session.commit()
        except:
            error = True
            print(sys.exc_info())
            db.session.rollback()
        finally:
            db.session.close()
            if error:
                flash(
                    'An error occurred. Artist '
                    + request.form['name']
                    + ' could not be listed.'
                )
            else:
                flash('Artist ' +
                      request.form['name'] + ' was successfully listed!')
    else:
        flash('Please! fill all fields with the correct format')
        flash(form.errors)
        return render_template('forms/new_artist.html', form=form)

    return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    data = []
    shows = Show.query.all()
    for show in shows:
        if show.start_time > datetime.now():
            venue = Venue.query.get(show.venue_id)
            artist = Artist.query.get(show.artist_id)
            data.append({"venue_id": show.venue_id,
                         "venue_name": venue.name,
                         "artist_id": show.artist_id,
                         "artist_name": artist.name,
                         "artist_image_link": artist.image_link,
                         "start_time": str(show.start_time)})
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    form = ShowForm()
    if form.validate_on_submit():
        try:
            new_show = Show(
                artist_id=request.form['artist_id'],
                venue_id=request.form['venue_id'],
                start_time=request.form['start_time'],
            )
            db.session.add(new_show)
            db.session.commit()
        except:
            db.session.rollback()
            error = True
            print(sys.exc_info())
        finally:
            db.session.close()
            if error:
                flash('An error occurred. The show could not be listed.')
            else:
                flash('Show was successfully listed!')
    else:
        flash('Please! fill all fields with the correct format')
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash(fieldName, err)
                print(fieldName, err)
        return render_template('forms/new_show.html', form=form)

    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
