from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from database import SessionLocal
import models
from schemas import ObservationCreate, ObservationUpdate, ObservationResponse
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


@router.get("/", tags=["Observations"])
def get_observations(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'observations', 'read')
        if user.role == 'farmer':
            observations = db.query(models.Observation).join(models.Field).filter(
                models.Field.user_id == user.user_id
            ).all()
        else:
            observations = db.query(models.Observation).all()
        return {"count": len(observations), "observations": [ObservationResponse.from_orm(o).dict() for o in observations]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get observations error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch observations")
    finally:
        db.close()


@router.get("/{observation_id}", tags=["Observations"])
def get_observation(observation_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'observations', 'read')
        observation = db.query(models.Observation).filter_by(observation_id=observation_id).first()
        if not observation:
            raise HTTPException(status_code=404, detail="Observation not found")
        if user.role == 'farmer':
            field = db.query(models.Field).filter_by(field_id=observation.field_id, user_id=user.user_id).first()
            if not field:
                raise HTTPException(status_code=403, detail="Access denied")
        return ObservationResponse.from_orm(observation).dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get observation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch observation")
    finally:
        db.close()


@router.post("/", status_code=201, tags=["Observations"])
def create_observation(obs_data: ObservationCreate, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'observations', 'create')
        field = db.query(models.Field).filter_by(field_id=obs_data.field_id).first()
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        satellite = db.query(models.Satellite).filter_by(satellite_id=obs_data.satellite_id).first()
        if not satellite:
            raise HTTPException(status_code=404, detail="Satellite not found")
        cycle = db.query(models.CropCycle).filter_by(cycle_id=obs_data.cycle_id).first()
        if not cycle:
            raise HTTPException(status_code=404, detail="Crop cycle not found")
        observation = models.Observation(
            field_id=obs_data.field_id,
            satellite_id=obs_data.satellite_id,
            cycle_id=obs_data.cycle_id,
            observation_date=obs_data.observation_date,
            cloud_cover=obs_data.cloud_cover,
        )
        db.add(observation)
        db.commit()
        db.refresh(observation)
        return {"message": "Observation created", "observation": ObservationResponse.from_orm(observation).dict()}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Create observation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create observation")
    finally:
        db.close()


@router.put("/{observation_id}", tags=["Observations"])
def update_observation(observation_id: int, obs_data: ObservationUpdate, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'observations', 'update')
        observation = db.query(models.Observation).filter_by(observation_id=observation_id).first()
        if not observation:
            raise HTTPException(status_code=404, detail="Observation not found")
        if obs_data.observation_date:
            observation.observation_date = obs_data.observation_date
        if obs_data.cloud_cover is not None:
            observation.cloud_cover = obs_data.cloud_cover
        if obs_data.satellite_id:
            observation.satellite_id = obs_data.satellite_id
        db.commit()
        db.refresh(observation)
        return {"message": "Observation updated", "observation": ObservationResponse.from_orm(observation).dict()}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Update observation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update observation")
    finally:
        db.close()


@router.delete("/{observation_id}", tags=["Observations"])
def delete_observation(observation_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'observations', 'delete')
        observation = db.query(models.Observation).filter_by(observation_id=observation_id).first()
        if not observation:
            raise HTTPException(status_code=404, detail="Observation not found")
        db.delete(observation)
        db.commit()
        return {"message": "Observation deleted"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Delete observation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete observation")
    finally:
        db.close()