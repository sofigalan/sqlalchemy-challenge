import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, distinct

from flask import Flask, jsonify

import datetime as dt
import numpy as np
import pandas as pd

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///titanic.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-01-01<br/>"
        f"/api/v1.0/2016-03-05/2016-03-20/summary<br/>"
        f"/api/v1.0/2016-03-05/2016-03-20"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
       session = Session(engine)
       max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
       max_date = max_date[0]

       min_date = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366) 

       query_result = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= min_date).\
                order_by(Measurement.date).\
                all()

       precipitation_dict = dict(query_result)

       return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
       session = Session(engine)
       stations_query_result = session.query(Measurement.station).group_by(Measurement.station).all()
       stations_list = list(np.ravel(stations_query_result))  # np.ravel flattens the nested array into a simple list
       return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
       session = Session(engine)
       max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
       max_date = max_date[0]
       min_date = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366)
       
       tobs_query_result = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= min_date).all()
       return jsonify(tobs_query_result)

@app.route("/api/v1.0/<start>")
def start(start):
       session = Session(engine)

       start_query_result = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
       start_list = list(start_query_result)
       return jsonify(start_list)

@app.route("/api/v1.0/<start_date>/<end_date>/summary")
def my_trip_sum(start_date, end_date):
       """
       
       """
       session = Session(engine)
       
       trip_query_result = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
       trip_list = list(trip_query_result)
       return jsonify(trip_list)

@app.route("/api/v1.0/<start_date>/<end_date>")
def my_trip_daily(start_date, end_date):
       """
       
       """
       session = Session(engine)
       
       trip_query_result = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).group_by(Measurement.date).all()
       trip_list = list(trip_query_result)
       return jsonify(trip_list)

if __name__ == "__main__":
   app.run(debug=True)
