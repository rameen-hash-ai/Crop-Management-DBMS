from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from database import SessionLocal
import models
from schemas import RegionCreate, RegionUpdate, RegionResponse
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


@router.get("/", tags=["Regions"])
def get_regions(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'regions', 'read')
        regions = db.query(models.Region).all()
        return {"count": len(regions), "regions": [RegionResponse.from_orm(r).dict() for r in regions]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get regions error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch regions")
    finally:
        db.close()


@router.get("/{region_id}", tags=["Regions"])
def get_region(region_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'regions', 'read')
        region = db.query(models.Region).filter_by(region_id=region_id).first()
        if not region:
            raise HTTPException(status_code=404, detail="Region not found")
        return RegionResponse.from_orm(region).dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get region error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch region")
    finally:
        db.close()


@router.post("/", status_code=201, tags=["Regions"])
def create_region(region_data: RegionCreate, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'regions', 'create')
        region = models.Region(
            region_name=region_data.region_name,
            climate_type=region_data.climate_type,
            latitude=region_data.latitude,
            longitude=region_data.longitude,
        )
        db.add(region)
        db.commit()
        db.refresh(region)
        return {"message": "Region created", "region": RegionResponse.from_orm(region).dict()}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Create region error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create region")
    finally:
        db.close()


@router.put("/{region_id}", tags=["Regions"])
def update_region(region_id: int, region_data: RegionUpdate, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'regions', 'update')
        region = db.query(models.Region).filter_by(region_id=region_id).first()
        if not region:
            raise HTTPException(status_code=404, detail="Region not found")
        if region_data.region_name:
            region.region_name = region_data.region_name
        if region_data.climate_type:
            region.climate_type = region_data.climate_type
        if region_data.latitude is not None:
            region.latitude = region_data.latitude
        if region_data.longitude is not None:
            region.longitude = region_data.longitude
        db.commit()
        db.refresh(region)
        return {"message": "Region updated", "region": RegionResponse.from_orm(region).dict()}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Update region error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update region")
    finally:
        db.close()


@router.delete("/{region_id}", tags=["Regions"])
def delete_region(region_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'regions', 'delete')
        region = db.query(models.Region).filter_by(region_id=region_id).first()
        if not region:
            raise HTTPException(status_code=404, detail="Region not found")
        db.delete(region)
        db.commit()
        return {"message": "Region deleted"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Delete region error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete region")
    finally:
        db.close()