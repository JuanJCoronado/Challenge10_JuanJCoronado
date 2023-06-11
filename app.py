# Import the dependencies.

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_
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
        f"<br/>"

        f"Static routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"

        f"<br/>"
        f"Dynamic routes:<br/>"
        f"/api/v1.0/<br/>"
        f"There are two ways in which information can be retrieved, mentioned below: <br/>"

        f"<br/>"
        f"Option 1: Retrieving information after a start date: write the start date after '/' in the format of yyyy - mm - dd. <br/>"
        f"For example: /api/v1.0/2016-03-15. This will retrieve data after 2016-03-15. <br/>"
        
        f"<br/>"
        f"Option 2: Retrieving information after a start date and before an end date: write the start date after '/' in the format of yyyy - mm - dd, and an end date after a second '/'.<br/>"
        f"For example: /api/v1.0/2016-03-15/2017-01-10. This will retrieve data after 2016-03-15 and before 2017-01-10. <br/>"  
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

@app.route("/api/v1.0/<start_date>")
def DynamicStart(start_date):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # get min, max, and avg data
    StartDateMinMaxAvg = (
    session
    .query(
        func.min(measurement_reflected.tobs),
        func.max(measurement_reflected.tobs),
        func.avg(measurement_reflected.tobs)
    )
    .filter(measurement_reflected.date > start_date)
    .all()
    )
    
    temperatures = []
    for minTemp, maxTemp, AvgTemp in StartDateMinMaxAvg:
        temperature_dict2 = {}
        temperature_dict2["minTemp"] = minTemp
        temperature_dict2["maxTemp"] = maxTemp
        temperature_dict2["avgTemp"] = AvgTemp
        temperatures.append(temperature_dict2)

    return jsonify(temperatures)

@app.route("/api/v1.0/<start_date>/<end_date>")
def DynamicStart_End(start_date, end_date):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # get min, max, and avg data
    StartEndDateMinMaxAvg = (
    session
    .query(
        func.min(measurement_reflected.tobs),
        func.max(measurement_reflected.tobs),
        func.avg(measurement_reflected.tobs)
    )
    .filter(
    and_(
        measurement_reflected.date > start_date,
        measurement_reflected.date < end_date
    )
    )
    )

    temperatures2 = []
    for minTemp, maxTemp, AvgTemp in StartEndDateMinMaxAvg:
        temperature_dict3 = {}
        temperature_dict3["minTemp"] = minTemp
        temperature_dict3["maxTemp"] = maxTemp
        temperature_dict3["avgTemp"] = AvgTemp
        temperatures2.append(temperature_dict3)

    return jsonify(temperatures2)


if __name__ == '__main__':
    app.run(debug=True)