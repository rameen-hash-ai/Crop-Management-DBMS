from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from database import SessionLocal
import models
from schemas import WeatherCreate, WeatherUpdate, WeatherResponse
from auth import RoleBasedAccessControl
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.get("/", tags=["Weather"])
def get_weather(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'weather', 'read')
        if user.role == 'farmer':
            records = db.query(models.Weather).join(models.Field).filter(
                models.Field.user_id == user.user_id
            ).all()
        else:
            records = db.query(models.Weather).all()
        return {"count": len(records), "weather": [WeatherResponse.from_orm(w).dict() for w in records]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get weather error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch weather")
    finally:
        db.close()


@router.get("/field/{field_id}", tags=["Weather"])
def get_field_weather(field_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'weather', 'read')
        field = db.query(models.Field).filter_by(field_id=field_id).first()
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        if user.role == 'farmer' and field.user_id != user.user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        records = db.query(models.Weather).filter_by(field_id=field_id).all()
        return {"field_id": field_id, "count": len(records), "weather": [WeatherResponse.from_orm(w).dict() for w in records]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get field weather error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch weather")
    finally:
        db.close()


@router.get("/{weather_id}", tags=["Weather"])
def get_weather_record(weather_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'weather', 'read')
        record = db.query(models.Weather).filter_by(weather_id=weather_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Weather record not found")
        return WeatherResponse.from_orm(record).dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get weather record error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch weather record")
    finally:
        db.close()


@router.post("/", status_code=201, tags=["Weather"])
def create_weather(weather_data: WeatherCreate, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'weather', 'create')
        field = db.query(models.Field).filter_by(field_id=weather_data.field_id).first()
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        record = models.Weather(
            field_id=weather_data.field_id,
            date=weather_data.date,
            temperature=weather_data.temperature,
            rainfall=weather_data.rainfall,
            humidity=weather_data.humidity,
            wind_speed=weather_data.wind_speed,
            wind_direction=weather_data.wind_direction,
            pressure=weather_data.pressure,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return {"message": "Weather record created", "weather": WeatherResponse.from_orm(record).dict()}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Create weather error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create weather record")
    finally:
        db.close()


@router.put("/{weather_id}", tags=["Weather"])
def update_weather(weather_id: int, weather_data: WeatherUpdate, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'weather', 'update')
        record = db.query(models.Weather).filter_by(weather_id=weather_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Weather record not found")
        for field_name, value in weather_data.dict(exclude_none=True).items():
            setattr(record, field_name, value)
        db.commit()
        db.refresh(record)
        return {"message": "Weather record updated", "weather": WeatherResponse.from_orm(record).dict()}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Update weather error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update weather record")
    finally:
        db.close()


@router.delete("/{weather_id}", tags=["Weather"])
def delete_weather(weather_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'weather', 'delete')
        record = db.query(models.Weather).filter_by(weather_id=weather_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Weather record not found")
        db.delete(record)
        db.commit()
        return {"message": "Weather record deleted"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Delete weather error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete weather record")
    finally:
        db.close()