from pydantic import BaseModel,EmailStr,field_validator
from typing import Optional
from datetime import datetime

#User Schemas
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
     longitude=Optional[float]=None

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

class fieldCreate(FieldBase):
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
     field_id=int
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
     