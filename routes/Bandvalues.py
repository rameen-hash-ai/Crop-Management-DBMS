from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from database import SessionLocal
import models
from schemas import BandValueCreate, BandValueUpdate, BandValueResponse
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


@router.get("/", tags=["Band Values"])
def get_band_values(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'band_values', 'read')
        values = db.query(models.Bandvalues).all()
        return {"count": len(values), "band_values": [BandValueResponse.from_orm(v).dict() for v in values]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get band values error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch band values")
    finally:
        db.close()


@router.get("/observation/{observation_id}", tags=["Band Values"])
def get_observation_band_values(observation_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'band_values', 'read')
        values = db.query(models.Bandvalues).filter_by(observation_id=observation_id).all()
        return {"observation_id": observation_id, "count": len(values),
                "band_values": [BandValueResponse.from_orm(v).dict() for v in values]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get observation band values error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch band values")
    finally:
        db.close()


@router.get("/{band_id}", tags=["Band Values"])
def get_band_value(band_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'band_values', 'read')
        value = db.query(models.Bandvalues).filter_by(band_id=band_id).first()
        if not value:
            raise HTTPException(status_code=404, detail="Band value not found")
        return BandValueResponse.from_orm(value).dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get band value error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch band value")
    finally:
        db.close()


@router.post("/", status_code=201, tags=["Band Values"])
def create_band_value(band_data: BandValueCreate, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'band_values', 'create')
        observation = db.query(models.Observation).filter_by(observation_id=band_data.observation_id).first()
        if not observation:
            raise HTTPException(status_code=404, detail="Observation not found")
        value = models.Bandvalues(
            observation_id=band_data.observation_id,
            band_name=band_data.band_name,
            band_value=band_data.band_value,
        )
        db.add(value)
        db.commit()
        db.refresh(value)
        return {"message": "Band value created", "band_value": BandValueResponse.from_orm(value).dict()}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Create band value error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create band value")
    finally:
        db.close()


@router.put("/{band_id}", tags=["Band Values"])
def update_band_value(band_id: int, band_data: BandValueUpdate, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'band_values', 'update')
        value = db.query(models.Bandvalues).filter_by(band_id=band_id).first()
        if not value:
            raise HTTPException(status_code=404, detail="Band value not found")
        if band_data.band_name:
            value.band_name = band_data.band_name
        if band_data.band_value is not None:
            value.band_value = band_data.band_value
        db.commit()
        db.refresh(value)
        return {"message": "Band value updated", "band_value": BandValueResponse.from_orm(value).dict()}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Update band value error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update band value")
    finally:
        db.close()


@router.delete("/{band_id}", tags=["Band Values"])
def delete_band_value(band_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'band_values', 'delete')
        value = db.query(models.Bandvalues).filter_by(band_id=band_id).first()
        if not value:
            raise HTTPException(status_code=404, detail="Band value not found")
        db.delete(value)
        db.commit()
        return {"message": "Band value deleted"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Delete band value error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete band value")
    finally:
        db.close()