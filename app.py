#dependencies
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#Connection to Sqlite DB
engine = create_engine("sqlite:///hawaii.sqlite")

#Initiate reflection object
Base = automap_base()

#Read database and create ORM objects
Base.prepare(engine, reflect=True)

#Save ORM objects to parameters
Measurement = Base.classes.measurement
Station = Base.classes.station

#Create the Flask Application
app = Flask(__name__)

#Homepage URL
@app.route("/")
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!<br>
    Available Routes:<br>
    <a href = "/api/v1.0/precipitation">/api/v1.0/precipitation</a><br>
    <a href = "/api/v1.0/stations">/api/v1.0/stations</a><br>
    <a href = "/api/v1.0/tobs">/api/v1.0/tobs</a><br>
    <a href = "/api/v1.0/temp/2017-06-01">/api/v1.0/temp/[start]</a><br>
    <a href = "/api/v1.0/temp/2017-06-01/2017-06-30">/api/v1.0/temp/[start]/[end]</a><br>
    ''')

#Print out the dictionary precipitation {date: precipitation}
@app.route("/api/v1.0/precipitation")
def precipitation():
    #open connection
    session = Session(engine)

    #get the previous year date
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #get data fromr Sqlite DB filter by date
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    #create dictionary 
    precip = {date: prcp for date, prcp in precipitation}
    
    #close connection
    session.close()
    
    #return JSON format with mimetype: application/json
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    #open connection
    session = Session(engine)

    #get stations from sqlite database
    results = session.query(Station.station).all()

    #flat-out data to list
    stations = list(np.ravel(results))

    #close connection
    session.close()
    
    #return JSON format with mimetype: application/json
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    #open connection
    session = Session(engine)

    #get the previous date
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #get temperatures from SQLite
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    
    #flat-out data to list
    temps = list(np.ravel(results))
    
    #close connection
    session.close()

    #return JSON format with mimetype: application/json
    return jsonify(temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    #open connection
    session = Session(engine)

    #Create the statistics list functions
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    #without submit end date, perform the query
    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)
    
    #with start and end dates, perform the query
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    
    #close connection
    session.close()

    #return JSON format with mimetype: application/json
    return jsonify(temps)

#execute the app only it is called directly
if __name__ == "__main__":
    app.run("",port=5000,debug=True)