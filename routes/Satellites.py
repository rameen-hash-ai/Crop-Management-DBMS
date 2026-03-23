from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from database import SessionLocal
import models
from schemas import SatelliteCreate, SatelliteUpdate, SatelliteResponse
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


@router.get("/", tags=["Satellites"])
def get_satellites(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'satellites', 'read')
        satellites = db.query(models.Satellite).all()
        return {"count": len(satellites), "satellites": [SatelliteResponse.from_orm(s).dict() for s in satellites]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get satellites error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch satellites")
    finally:
        db.close()


@router.get("/{satellite_id}", tags=["Satellites"])
def get_satellite(satellite_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'satellites', 'read')
        satellite = db.query(models.Satellite).filter_by(satellite_id=satellite_id).first()
        if not satellite:
            raise HTTPException(status_code=404, detail="Satellite not found")
        return SatelliteResponse.from_orm(satellite).dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get satellite error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch satellite")
    finally:
        db.close()


@router.post("/", status_code=201, tags=["Satellites"])
def create_satellite(satellite_data: SatelliteCreate, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'satellites', 'create')
        satellite = models.Satellite(
            satellite_name=satellite_data.satellite_name,
            provider=satellite_data.provider,
            resolution=satellite_data.resolution,
        )
        db.add(satellite)
        db.commit()
        db.refresh(satellite)
        return {"message": "Satellite created", "satellite": SatelliteResponse.from_orm(satellite).dict()}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Create satellite error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create satellite")
    finally:
        db.close()


@router.put("/{satellite_id}", tags=["Satellites"])
def update_satellite(satellite_id: int, satellite_data: SatelliteUpdate, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'satellites', 'update')
        satellite = db.query(models.Satellite).filter_by(satellite_id=satellite_id).first()
        if not satellite:
            raise HTTPException(status_code=404, detail="Satellite not found")
        if satellite_data.satellite_name:
            satellite.satellite_name = satellite_data.satellite_name
        if satellite_data.provider:
            satellite.provider = satellite_data.provider
        if satellite_data.resolution is not None:
            satellite.resolution = satellite_data.resolution
        db.commit()
        db.refresh(satellite)
        return {"message": "Satellite updated", "satellite": SatelliteResponse.from_orm(satellite).dict()}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Update satellite error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update satellite")
    finally:
        db.close()


@router.delete("/{satellite_id}", tags=["Satellites"])
def delete_satellite(satellite_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'satellites', 'delete')
        satellite = db.query(models.Satellite).filter_by(satellite_id=satellite_id).first()
        if not satellite:
            raise HTTPException(status_code=404, detail="Satellite not found")
        db.delete(satellite)
        db.commit()
        return {"message": "Satellite deleted"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Delete satellite error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete satellite")
    finally:
        db.close()