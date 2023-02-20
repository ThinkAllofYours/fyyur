# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import ForeignKey
from forms import *
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional


# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db = SQLAlchemy()
migrate = Migrate()
# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = "Venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.Text)
    website_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)

    shows = db.relationship("Show", backref="Venue", lazy=True)

    def __repr__(self):
        return f"<Venue {self.id} {self.name}>"


class Artist(db.Model):
    __tablename__ = "Artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.Text)

    shows = db.relationship("Show", backref="Artist", lazy=True)

    def __repr__(self):
        return f"<Artist {self.id} {self.name}>"


class Show(db.Model):
    __tablename__ = "Show"

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<Show {self.id} {self.start_time} aritst {self.artist_id} venue {self.venue_id}>"


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
with app.app_context():
    db.init_app(app)
    migrate.init_app(app, db)
    db.create_all()

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    venues = Venue.query.all()
    data = {}
    for venue in venues:
        if venue.city not in data:
            data[venue.city] = {"city": venue.city, "state": venue.state, "venues": []}
        data[venue.city]["venues"].append(
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(
                    [show for show in venue.shows if show.start_time > datetime.now()]
                ),
            }
        )
    data = list(data.values())
    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    search_term = request.form.get("search_term", "")
    venues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
    data = []
    for venue in venues:
        data.append(
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(
                    [show for show in venue.shows if show.start_time > datetime.now()]
                ),
            }
        )
    response = {"count": len(venues), "data": data}
    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    return render_template("pages/show_venue.html", venue=venue)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    name = request.form.get("name")
    city = request.form.get("city")
    state = request.form.get("state")
    address = request.form.get("address")
    phone = request.form.get("phone")
    image_link = request.form.get("image_link")
    genres = request.form.getlist("genres")
    facebook_link = request.form.get("facebook_link")
    website_link = request.form.get("website_link")
    seeking_talent = request.form.get("seeking_talent")
    seeking_description = request.form.get("seeking_description")

    venue = Venue(
        name=name,
        city=city,
        state=state,
        address=address,
        phone=phone,
        image_link=image_link,
        genres=genres,
        facebook_link=facebook_link,
        website_link=website_link,
        seeking_talent=seeking_talent == "y",
        seeking_description=seeking_description,
    )

    db.session.add(venue)
    try:
        db.session.commit()
        flash("Venue " + request.form["name"] + " was successfully listed!")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred. Venue " + request.form["name"] + " could not be listed.")
        print(e)
    return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    # TODO: replace with real data returned from querying the database
    artists = db.session.query(Artist.id, Artist.name).all()
    return render_template("pages/artists.html", artists=artists)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    search_term = request.form.get("search_term", "")
    artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
    data = []
    for artist in artists:
        data.append(
            {
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": len(
                    [show for show in artist.shows if show.start_time > datetime.now()]
                ),
            }
        )
    response = {"count": len(artists), "data": data}
    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get_or_404(artist_id)
    return render_template("pages/show_artist.html", artist=artist)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm(obj=artist)
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get_or_404(artist_id)
    for field in request.form:
        if field == "genres":
            setattr(artist, field, request.form.getlist(field))
        elif field == "seeking_venue":
            setattr(artist, field, request.form.get(field) == "y")
        else:
            setattr(artist, field, request.form.get(field))
    try:
        db.session.add(artist)
        db.session.commit()
        flash("Artist " + request.form["name"] + " was successfully updated!")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred. Artist " + request.form["name"] + " could not be updated.")
    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    form = VenueForm(obj=venue)
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    for field in request.form:
        if field == "genres":
            setattr(venue, field, request.form.getlist(field))
        elif field == "seeking_talent":
            setattr(venue, field, request.form.get(field) == "y")
        else:
            setattr(venue, field, request.form.get(field))
    try:
        db.session.add(venue)
        db.session.commit()
        flash("Venue " + request.form["name"] + " was successfully updated!")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred. Venue " + request.form["name"] + " could not be updated.")
    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    name = request.form.get("name")
    city = request.form.get("city")
    state = request.form.get("state")
    phone = request.form.get("phone")
    genres = request.form.getlist("genres")
    facebook_link = request.form.get("facebook_link")
    image_link = request.form.get("image_link")
    website_link = request.form.get("website_link")
    seeking_venue = request.form.get("seeking_venue")
    seeking_description = request.form.get("seeking_description")

    artist = Artist(
        name=name,
        city=city,
        state=state,
        phone=phone,
        genres=genres,
        facebook_link=facebook_link,
        image_link=image_link,
        website_link=website_link,
        seeking_venue=seeking_venue == "y",
        seeking_description=seeking_description,
    )

    db.session.add(artist)
    try:
        db.session.commit()
        flash("Artist " + request.form["name"] + " was successfully listed!")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred. Artist " + request.form["name"] + " could not be listed.")
    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    shows = Show.query.all()
    data = []
    for show in shows:
        data.append(
            {
                "venue_id": show.venue_id,
                "venue_name": show.Venue.name,
                "artist_id": show.artist_id,
                "artist_name": show.Artist.name,
                "artist_image_link": show.Artist.image_link,
                "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    artist_id = request.form.get("artist_id")
    venue_id = request.form.get("venue_id")
    start_time = request.form.get("start_time")
    show = Show(
        artist_id=artist_id,
        venue_id=venue_id,
        start_time=start_time,
    )
    db.session.add(show)
    try:
        db.session.commit()
        flash("Show was successfully listed!")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred. Show could not be listed.")
    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
