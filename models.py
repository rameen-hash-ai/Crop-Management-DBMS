#converting the boxes and lines from our ER diagram into python classes
from sqlalchemy import Column,Integer,String,Float,ForeignKey,Date,VARCHAR
from database import base   
from sqlalchemy.orm import relationship

class User(base):
    __tablename__="users"
    user_id=Column(Integer,primary_key=True,index=True)
    name=Column(String)
    role=Column(String)
    email=Column(String,unique=True)

    fields=relationship("Field",back_populates="owner")

class Field(base):
    __tablename__="fields"
    field_id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("users.user_id"))
    region_id=Column(Integer,ForeignKey("regions.region_id"))
    latitude=Column(Float)
    longitude=Column(Float)
    area=Column(Float)
    soil_type=Column(String)

    owner=relationship("User",back_populates="fields")
    region=relationship("Region",back_populates="fields")
    crop_cycles=relationship("CropCycle",back_populates="fields")
    weather_data=relationship("Weather",back_populates="fields")
    alert=relationship("Alert",back_populates="fields")


class region(base):
    __tablename__="region"
    region_id=Column(Integer,primary_key=True,indx=True)
    region_name=Column(String)
    climate_type=Column(String)

    fields=relationship("Field",back_populates="region")

class Satellite(base):
    __tablename__="Satellite"
    satellite_id=Column(Integer,primary_key=True,index=True)
    satellite_name=Column(String)
    provider=Column(String)
    resolution=Column(Float)

    crop_cycles=relationship("CropCycle",back_populates="satellite")
class CropCycle(base):
    __tablename__="crop_cycle"
    cycle_id=Column(Integer,primary_key=True,index=True)
    field_id=Column(Integer,ForeignKey("fields.field_id"))
    crop_name=Column(String)
    start_date=(Column(Date))
    expected_harvest_date=Column(Date)


    fields=relationship("Field",back_populates="crop_cycles")
    satellite=relationship("Satellite",back_populates="crop_cycles")

class Weather(base):
    __tablename__="weather"
    weather_id=Column(Integer,primary_key=True,index=True)
    field_id=Column(Integer,ForeignKey("fields.field_id"))
    date=Column(Date)
    temperature=Column(Float)
    humidity=Column(Float)
    rainfall=Column(Float)

    fields=relationship("Field",back_populates="weather_data")
class Observation(base):
    __tablename__="observation"
    observation_id=Column(Integer,primary_key=True,index=True)
    field_id=Column(Integer,ForeignKey("fields.field_id"))
    satellite_id=Column(Integer,ForeignKey("Satellite.satellite_id"))
    cycle_id=Column(Integer,ForeignKey("crop_cycle.cycle_id"))
    observation_date=Column(Date)
    cloud_cover=Column(Float)

    fields=relationship("Field",back_populates="observations")
    satellite_id=relationship("Satellite",back_populates="observations")
    crop_cycle=relationship("CropCycle",back_populates="observations")

class Bandvalues(base):
    __tablename__="bandvalues"
    band_id=Column(Integer,primary_key=True,index=True)
    observation_id=Column(Integer,ForeignKey("observation.observation_id"))
    band_name=Column(String)
    band_value=Column(Float)

    observation=relationship("Observation",back_populates="bandvalues")

class DerivedMetrics(base):
    __tablename__="derived_metrics"
    metric_id=Column(Integer,primary_key=True,index=True)
    observation_id=Column(Integer,ForeignKey("observation.observation_id"))
    ndvi=Column(Float)
    evi=Column(Float)
    soil_moisture=Column(Float)
    crop_health_score=Column(Float)

    observation=relationship("Observation",back_populates="derived_metrics")

class Alert(base):
    __tablename__="alert"
    alert_id=Column(Integer,primary_key=True,index=True)
    field_id=Column(Integer,ForeignKey("fields.field_id"))
    observation_id=Column(Integer,ForeignKey("observation.observation_id"))
    alert_type=Column(String)
    severity=Column(String)
    message=Column(String)
    
    fields=relationship("Field",back_populates="alert")