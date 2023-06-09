# Import the dependencies.

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model

Base = automap_base()

# reflect the tables

Base.prepare(autoload_with=engine)

# Save references to each table
measurement_reflected = Base.classes.measurement
station_reflected = Base.classes.station

# Create our session (link) from Python to the DB
# session = Session(engine) - this goes down on each route

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    print('Home')
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs"
    )
@app.route("/api/v1.0/precipitation")
def prec():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the most recent date in the data set.
    latest_date = (
    session
    .query(measurement_reflected.date)
    .order_by(measurement_reflected.date.desc())
    .first()
    )

    # Calculate Previous Year Date
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Get all data from previous year to latest date in dataset.
    last_12_months = (
    session
    .query(
        measurement_reflected.date,
        measurement_reflected.prcp
    )
    .filter(measurement_reflected.date > prev_year)
    .order_by(measurement_reflected.date)
    )
    
    session.close()

    # Create a dictionary from the row data and append to a list of all_precipitations
    all_precipitations = []
    for date, prcp in last_12_months:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitations.append(precipitation_dict)

    return jsonify(all_precipitations)

@app.route("/api/v1.0/stations")
def stat():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # List the stations and their counts in descending order.
    stations_info = (
    session
    .query(
        station_reflected.id, station_reflected.station, station_reflected.name,
        station_reflected.latitude, station_reflected.longitude, station_reflected.elevation
    )
    .all()
    )
    
    session.close()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for id, station, name, latitude, longitude, elevation in stations_info:
        stations_dict = {}
        stations_dict["id"] = id
        stations_dict["station"] = station
        stations_dict["name"] = name
        stations_dict["latitude"] = latitude
        stations_dict["longitude"] = longitude
        stations_dict["elevation"] = elevation
        all_stations.append(stations_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate Previous Year Date
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   
   
    MostActive_last_12_months_temp = (
    session
    .query(
        measurement_reflected.date,
        measurement_reflected.tobs
    )
    .filter(
        (measurement_reflected.date > prev_year), 
        (measurement_reflected.station == 'USC00519281')
    )
    .all()
    )

    session.close()

    # Create a dictionary from the row data and append to a list of all_precipitations
    all_temperatures = []
    for date, tobs in MostActive_last_12_months_temp:
        temperature_dict = {}
        temperature_dict["date"] = date
        temperature_dict["tobs"] = tobs
        all_temperatures.append(temperature_dict)

    return jsonify(all_temperatures)


if __name__ == '__main__':
    app.run(debug=True)