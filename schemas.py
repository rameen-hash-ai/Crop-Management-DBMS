from pydantic import BaseModel,EmailStr,field_validator
from typing import Optional
from datetime import datetime
#hello
#User Schemas
#Base = What user enters
# Create = Base + required relationships
# Update = Everything optional
# Response = Base + what DB generates
# Pass = Class has nothing unique to add
print("HELLO FROM REAL FILE")
class UserBase(BaseModel):
    #base user schema with common fields for user creation and update
    name:str
    email:EmailStr
    role:str="farmer"

class UserCreate(UserBase):
    #schema for user registration with password field
    password:str
    @field_validator("password")
    @classmethod
    def validate_password(cls,password):
        if len(password)<8:
            raise ValueError("Password must be at least 8 characters")
        return password
class UserLogin(BaseModel):
        #schema for user login with email and password
        email:EmailStr
        password:str
class UserResponse(UserBase):
        #schema for user response without password
        user_id:int
        is_active:bool
        created_at:datetime
        class Config:
            from_attributes=True

class LoginResponse(BaseModel):
    #schema for login response with user details and token
    access_token:str
    token_type:str="bearer"
    user:UserResponse

class RegionBase(BaseModel):
    region_name:str
    climate_type:str

class RegionCreate(RegionBase):
     latitude:Optional[float]=None
     longitude:Optional[float]=None

class RegionResponse(RegionBase):
    region_id:int
    class Config:
        from_attributes=True

class FieldBase(BaseModel):
    #human entered data goes here
    latitude:float
    longitude:float
    area:float
    soil_type:str
    region_id:int
    field_name:str

class FieldCreate(FieldBase):
    #the user must provide this info in order to create a field
    user_id:int
    region_id:int
class FieldResponse(FieldBase):
    #this information is sent back to the client,Database generates it
    field_id:int
    user_id:int
    region_id:int   
    is_active:bool
    created_at:datetime
    class Config:
        from_attributes=True

class CropCycleBase(BaseModel):
     crop_name:str
     field_id:int
     start_date:datetime
     expected_harvest_date:datetime

class CropCycleCreate(CropCycleBase):
     field_id:int

class CropCycleResponse(CropCycleBase):
        cycle_id:int
        field_id:int
        status:str
        actual_harvest_date:Optional[datetime]=None
        created_at:datetime
        class Config:
            from_attributes=True
class BandValueBase(BaseModel):
     band_name:str
     band_value:float

class BandValueCreate(BandValueBase):
     observation_id:int
     band_id:int

class BandValueResponse(BandValueBase):
     band_value_id:int
     observation_id:int
     band_id:int
     created_at:datetime
     class Config:
         from_attributes=True

#User Update Schema
class UserUpdate(BaseModel):
     name:Optional[str]=None
     email:Optional[EmailStr]=None
     role:Optional[str]=None
     password:Optional[str]=None
     is_active:Optional[bool]=None
     @field_validator("password")
     @classmethod
     def validate_password(cls,password):
          if password and len(password)<8:
               raise ValueError("Password must be at least 8 characters")
          return password

#Region Update Schema
class RegionUpdate(BaseModel):
     region_name:Optional[str]=None
     climate_type:Optional[str]=None
     latitude:Optional[float]=None
     longitude:Optional[float]=None

#Field Update Schema
class FieldUpdate(BaseModel):
     latitude:Optional[float]=None
     longitude:Optional[float]=None
     area:Optional[float]=None
     soil_type:Optional[str]=None
     field_name:Optional[str]=None
     region_id:Optional[int]=None
     is_active:Optional[bool]=None

#CropCycle Update Schema
class CropCycleUpdate(BaseModel):
     crop_name:Optional[str]=None
     start_date:Optional[datetime]=None
     expected_harvest_date:Optional[datetime]=None
     status:Optional[str]=None
     actual_harvest_date:Optional[datetime]=None

#BandValue Update Schema
class BandValueUpdate(BaseModel):
     band_name:Optional[str]=None
     band_value:Optional[float]=None
     
class AlertBase(BaseModel):
    alert_type:str
    severity:str
    message:str
    field_id:int
class AlertCreate(AlertBase):
    field_id:int
    observation_id:Optional[int]=None
class AlertUpdate(BaseModel):
    alert_type:Optional[str]=None
    severity:Optional[str]=None
    message:Optional[str]=None
    is_resolved:Optional[bool]=None
    resolved_at:Optional[datetime]=None
class AlertResponse(AlertBase):
    alert_id:int
    field_id:int
    observation_id:Optional[int]=None
    is_resolved:bool
    resolved_at:Optional[datetime]=None
    created_at:datetime
    class Config:
        from_attributes=True
class SatelliteBase(BaseModel):
    satellite_name:str
    provider:str
    resolution:float

class SatelliteCreate(SatelliteBase):
    pass

class SatlliteResponse(SatelliteBase):
        satellite_id:int
        created_at:datetime
        class Config:
            from_attributes=True
class SatelliteUpdate(BaseModel):
    satellite_name:Optional[str]=None
    provider:Optional[str]=None
    resolution:Optional[float]=None

class ObservationBase(BaseModel):
     field_id:int
     satellite_id:int
     cycle_id:int
     observation_date:datetime
     cloud_cover:float
class ObservationCreate(ObservationBase):
     field_id:int
     satellite_id:int
     cycle_id:int
class ObservationUpdate(BaseModel):
    field_id:Optional[int]=None
    satellite_id:Optional[int]=None
    cycle_id:Optional[int]=None
    observation_date:Optional[datetime]=None
    cloud_cover:Optional[float]=None
class ObservationResponse(ObservationBase):
    observation_id:int
    created_at:datetime
    class Config:
        from_attributes=True

class DerivedMetricsBase(BaseModel):
     observation_id:int
     ndvi:float
     evi:float
     soil_moisture:float
     crop_health_score:float
class DerivedMetricsCreate(DerivedMetricsBase):
     observation_id:int
class DerivedMetricsUpdate(BaseModel):
    observation_id:Optional[int]=None
    ndvi:Optional[float]=None
    evi:Optional[float]=None
    soil_moisture:Optional[float]=None
    crop_health_score:Optional[float]=None
class DerivedMetricsResponse(DerivedMetricsBase):
    metric_id:int
    created_at:datetime
    class Config:
        from_attributes=True
class WeatherBase(BaseModel):
     field_id:int
     date:datetime
     temperature:str
     rainfall:str
     humidity:str
     wind_speed:Optional[str]=None
     wind_direction:Optional[str]=None
     pressure:Optional[str]=None
class WeatherCreate(WeatherBase):
     field_id:int   

class WeatherUpdate(BaseModel):
    field_id:Optional[int]=None
    date:Optional[datetime]=None
    temperature:Optional[str]=None
    rainfall:Optional[str]=None
    humidity:Optional[str]=None
    wind_speed:Optional[str]=None
    wind_direction:Optional[str]=None
    pressure:Optional[str]=None
class WeatherResponse(WeatherBase):
    weather_id:int
    created_at:datetime
    class Config:
        from_attributes=True


    