#converting the boxes and lines from our ER diagram into python classes
from sqlalchemy import Boolean, Column, DateTime,Integer,String,Float,ForeignKey,Date,VARCHAR
from database import base   
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime
from enum import Enum as PyEnum
import uuid

# ======================= Enums it helps defining fixed set of values for a column in the database =======================  

class UserRole(PyEnum):
    FARMER="FARMER"
    AGRONOMIST="AGRONOMIST"
    ADMIN="ADMIN"
class ClimateType(PyEnum):
    ARID="ARID"
    SEMI_ARID="SEMI_ARID"
    TEMPERATE="TEMPERATE"
    TROPICAL="TROPICAL"
class AlertSeverity(PyEnum):
    LOW="LOW"
    MEDIUM="MEDIUM"
    HIGH="HIGH"
    CRITICAL="CRITICAL"

class CycleStatus(PyEnum):
    PLANTED="PLANTED"
    GROWING="GROWING"
    HARVESTED="HARVESTED"

class CropType(PyEnum):
    WHEAT="WHEAT"
    CORN="CORN"
    RICE="RICE"
    SUGAR_CANE="SUGAR_CANE" 
class SoilType(PyEnum):
    SANDY="SANDY"
    CLAY="CLAY"
    SILTY="SILTY"
    LOAMY="LOAMY"
class SatelliteProvider(PyEnum):
    NASA="NASA"
    ESA="ESA"
    JAXA="JAXA"
    ISRO="ISRO"
class SatelliteType(PyEnum):
    OPTICAL="OPTICAL"
    RADAR="RADAR"
    THERMAL="THERMAL"
class CropHealthScore(PyEnum):
    EXCELLENT="EXCELLENT"
    GOOD="GOOD"
    FAIR="FAIR"
    POOR="POOR"

class ObservationType(PyEnum):
    NDVI="NDVI"
    EVI="EVI"
    SOIL_MOISTURE="SOIL_MOISTURE"

class AlertType(PyEnum):
    PEST_INFESTATION="PEST_INFESTATION"
    DISEASE_OUTBREAK="DISEASE_OUTBREAK"
    WATER_STRESS="WATER_STRESS"
    NUTRIENT_DEFICIENCY="NUTRIENT_DEFICIENCY"


# ======================= Database Models =======================
class User(base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    role = Column(String(50), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
 
    fields = relationship("Field", back_populates="owner", cascade="all,delete-orphan")
 
    def __repr__(self):
        return f"<User {self.name} ({self.role})>"
 
 
class Field(base):
    __tablename__ = "fields"
    field_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    region_id = Column(Integer, ForeignKey("region.region_id"))
    field_name = Column(String(150), nullable=True)       
    latitude = Column(Float(20), nullable=False)
    longitude = Column(Float(20), nullable=False)
    area = Column(Float(20), nullable=False)
    soil_type = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)              
    created_at = Column(DateTime, default=datetime.utcnow) 
 
    owner = relationship("User", back_populates="fields")
    region = relationship("Region", back_populates="fields")
    crop_cycles = relationship("CropCycle", back_populates="fields", cascade="all,delete-orphan")
    weather_data = relationship("Weather", back_populates="fields")
    observations = relationship("Observation", back_populates="fields")
    alerts = relationship("Alert", back_populates="field")
 
 
class Region(base):
    __tablename__ = "region"
    region_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    region_name = Column(String(150), nullable=False)
    climate_type = Column(String(50), nullable=False)
    latitude = Column(Float(20), nullable=True)
    longitude = Column(Float(20), nullable=True)
 
    fields = relationship("Field", back_populates="region")
 
 
class Satellite(base):
    __tablename__ = "satellite"
    satellite_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    satellite_name = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)
    resolution = Column(Float(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)  
 
    observations = relationship("Observation", back_populates="satellite")
 
 
class CropCycle(base):
    __tablename__ = "crop_cycle"
    cycle_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    field_id = Column(Integer, ForeignKey("fields.field_id"))
    crop_name = Column(String(100), nullable=False)
    start_date = Column(String(20), nullable=False)
    expected_harvest_date = Column(String(20), nullable=False)
    status = Column(String(50), default="active")          
    actual_harvest_date = Column(String(20), nullable=True) # 
    created_at = Column(DateTime, default=datetime.utcnow)  #
 
    fields = relationship("Field", back_populates="crop_cycles")
    observations = relationship("Observation", back_populates="crop_cycle")
 
 
class Weather(base):
    __tablename__ = "weather"
    weather_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    field_id = Column(Integer, ForeignKey("fields.field_id"))
    date = Column(String(20), nullable=False, index=True)
    temperature = Column(String(10), nullable=False)
    rainfall = Column(String(10), nullable=False)
    humidity = Column(String(10), nullable=False)
    wind_speed = Column(String(10), nullable=True)
    wind_direction = Column(String(10), nullable=True)
    pressure = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)  
 
    fields = relationship("Field", back_populates="weather_data")
 
 
class Observation(base):
    __tablename__ = "observation"
    observation_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    field_id = Column(Integer, ForeignKey("fields.field_id"))
    satellite_id = Column(Integer, ForeignKey("satellite.satellite_id"))
    cycle_id = Column(Integer, ForeignKey("crop_cycle.cycle_id"))
    observation_date = Column(String(20), nullable=False)
    cloud_cover = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)  
 
    fields = relationship("Field", back_populates="observations")
    satellite = relationship("Satellite", back_populates="observations")
    crop_cycle = relationship("CropCycle", back_populates="observations")
    bandvalues = relationship("Bandvalues", back_populates="observation", cascade="all,delete-orphan")
    derived_metrics = relationship("DerivedMetrics", back_populates="observation", cascade="all,delete-orphan")
    alerts = relationship("Alert", back_populates="observation", cascade="all,delete-orphan")
 
 
class Bandvalues(base):
    __tablename__ = "bandvalues"
    band_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    observation_id = Column(Integer, ForeignKey("observation.observation_id"))
    band_name = Column(String(150), nullable=False)
    band_value = Column(Float(40), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
 
    observation = relationship("Observation", back_populates="bandvalues")
 
 
class DerivedMetrics(base):
    __tablename__ = "derived_metrics"
    metric_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    observation_id = Column(Integer, ForeignKey("observation.observation_id"))
    ndvi = Column(Float)
    evi = Column(Float)
    soil_moisture = Column(Float)
    crop_health_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
 
    observation = relationship("Observation", back_populates="derived_metrics")
 
 
class Alert(base):
    __tablename__ = "alert"
    alert_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    field_id = Column(Integer, ForeignKey("fields.field_id", ondelete="CASCADE"), nullable=False)
    observation_id = Column(Integer, ForeignKey("observation.observation_id", ondelete="SET NULL"), nullable=True)
    alert_type = Column(String(100), nullable=False, index=True)
    severity = Column(String(50), nullable=False)
    message = Column(String(500), nullable=False)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
 
    field = relationship("Field", back_populates="alerts")
    observation = relationship("Observation", back_populates="alerts")
 