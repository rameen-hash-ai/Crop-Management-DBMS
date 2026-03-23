
#hello
#User Schemas
#Base = What user enters
# Create = Base + required relationships
# Update = Everything optional
# Response = Base + what DB generates
# Pass = Class has nothing unique to add
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


# ======================= User Schemas =======================

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str = "farmer"

class UserCreate(UserBase):
    password: str
    @field_validator("password")
    @classmethod
    def validate_password(cls, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        return password

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    user_id: int
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    @field_validator("password")
    @classmethod
    def validate_password(cls, password):
        if password and len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        return password

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ======================= Region Schemas =======================

class RegionBase(BaseModel):
    region_name: str
    climate_type: str

class RegionCreate(RegionBase):
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class RegionUpdate(BaseModel):
    region_name: Optional[str] = None
    climate_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class RegionResponse(RegionBase):
    region_id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    class Config:
        from_attributes = True


# ======================= Field Schemas =======================

class FieldBase(BaseModel):
    latitude: float
    longitude: float
    area: float
    soil_type: str
    region_id: int
    field_name: Optional[str] = None  # ✅ optional so old data without names doesn't crash

class FieldCreate(FieldBase):
    user_id: int

class FieldUpdate(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area: Optional[float] = None
    soil_type: Optional[str] = None
    field_name: Optional[str] = None
    region_id: Optional[int] = None
    is_active: Optional[bool] = None

class FieldResponse(FieldBase):
    field_id: int
    user_id: int
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True


# ======================= Crop Cycle Schemas =======================

class CropCycleBase(BaseModel):
    crop_name: str
    field_id: int
    start_date: str          # ✅ str not datetime — model stores as String
    expected_harvest_date: str

class CropCycleCreate(CropCycleBase):
    pass

class CropCycleUpdate(BaseModel):
    crop_name: Optional[str] = None
    start_date: Optional[str] = None
    expected_harvest_date: Optional[str] = None
    status: Optional[str] = None
    actual_harvest_date: Optional[str] = None

class CropCycleResponse(CropCycleBase):
    cycle_id: int
    status: str
    actual_harvest_date: Optional[str] = None  # ✅ str not datetime — model stores as String
    created_at: datetime
    class Config:
        from_attributes = True


# ======================= Satellite Schemas =======================

class SatelliteBase(BaseModel):
    satellite_name: str
    provider: str
    resolution: float

class SatelliteCreate(SatelliteBase):
    pass

class SatelliteUpdate(BaseModel):
    satellite_name: Optional[str] = None
    provider: Optional[str] = None
    resolution: Optional[float] = None

class SatelliteResponse(SatelliteBase):   # ✅ fixed typo — was SatlliteResponse
    satellite_id: int
    created_at: datetime
    class Config:
        from_attributes = True


# ======================= Observation Schemas =======================

class ObservationBase(BaseModel):
    field_id: int
    satellite_id: int
    cycle_id: int
    observation_date: str    # ✅ str — model stores as String
    cloud_cover: float

class ObservationCreate(ObservationBase):
    pass

class ObservationUpdate(BaseModel):
    field_id: Optional[int] = None
    satellite_id: Optional[int] = None
    cycle_id: Optional[int] = None
    observation_date: Optional[str] = None
    cloud_cover: Optional[float] = None

class ObservationResponse(ObservationBase):
    observation_id: int
    created_at: datetime
    class Config:
        from_attributes = True


# ======================= Band Value Schemas =======================

class BandValueBase(BaseModel):
    band_name: str
    band_value: float

class BandValueCreate(BandValueBase):
    observation_id: int

class BandValueUpdate(BaseModel):
    band_name: Optional[str] = None
    band_value: Optional[float] = None

class BandValueResponse(BandValueBase):
    band_id: int              # ✅ fixed — model PK is band_id not band_value_id
    observation_id: int
    created_at: datetime
    class Config:
        from_attributes = True


# ======================= Derived Metrics Schemas =======================

class DerivedMetricsBase(BaseModel):
    observation_id: int
    ndvi: float
    evi: float
    soil_moisture: float
    crop_health_score: float

class DerivedMetricsCreate(DerivedMetricsBase):
    pass

class DerivedMetricsUpdate(BaseModel):
    ndvi: Optional[float] = None
    evi: Optional[float] = None
    soil_moisture: Optional[float] = None
    crop_health_score: Optional[float] = None

class DerivedMetricsResponse(DerivedMetricsBase):
    metric_id: int
    created_at: datetime
    class Config:
        from_attributes = True


# ======================= Weather Schemas =======================

class WeatherBase(BaseModel):
    field_id: int
    date: str                # ✅ str — model stores as String
    temperature: str
    rainfall: str
    humidity: str
    wind_speed: Optional[str] = None
    wind_direction: Optional[str] = None
    pressure: Optional[str] = None

class WeatherCreate(WeatherBase):
    pass

class WeatherUpdate(BaseModel):
    date: Optional[str] = None
    temperature: Optional[str] = None
    rainfall: Optional[str] = None
    humidity: Optional[str] = None
    wind_speed: Optional[str] = None
    wind_direction: Optional[str] = None
    pressure: Optional[str] = None

class WeatherResponse(WeatherBase):
    weather_id: int
    created_at: datetime
    class Config:
        from_attributes = True


# ======================= Alert Schemas =======================

class AlertBase(BaseModel):
    alert_type: str
    severity: str
    message: str
    field_id: int

class AlertCreate(AlertBase):
    observation_id: Optional[int] = None

class AlertUpdate(BaseModel):
    alert_type: Optional[str] = None
    severity: Optional[str] = None
    message: Optional[str] = None
    is_resolved: Optional[bool] = None
    resolved_at: Optional[datetime] = None

class AlertResponse(AlertBase):
    alert_id: int
    observation_id: Optional[int] = None
    is_resolved: bool
    resolved_at: Optional[datetime] = None
    created_at: datetime
    class Config:
        from_attributes = True