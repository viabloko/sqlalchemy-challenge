# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (f"Please, see the available API routes below<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start> and /api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query the recent date and the data
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    last_year = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    prcp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year).\
    group_by(Measurement.date).all()
    session.close()
    #Create dictionary
    precip = {date: prcp for date, prcp in prcp}

    return jsonify(precip)

@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #Query
    stations = session.query(Station.station).all()
    session.close()
    stations = list(np.ravel(stations))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tob():
    # Create our session (link) from Python to the DB
    session = Session(engine)
   # Query the recent date and the data
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    last_year = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    #The most active station
    active = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()
    #Query temperature data for the last year for this station
    temperatures = session.query(Measurement.tobs).filter(Measurement.station == active[0][0]).\
    filter(Measurement.date >= last_year).all()
    
    tobs = list(np.ravel(temperatures))
    session.close()
    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def start(start=None):
    start = dt.datetime.strptime(start, "%m%d%Y")
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).all()
    tstats = list(np.ravel(results))
    session.close()
    return jsonify(tstats)

@app.route("/api/v1.0/<start>/<end>")
def end(start=None, end=None):
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")
    session = Session(engine)
    results2 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date <= end).filter(Measurement.date >= start).all()
    tstats2 = list(np.ravel(results2))
    session.close()
    return jsonify(tstats2)

if __name__ == "__main__":
    app.run(debug=True)
