from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from database import SessionLocal
import models
from schemas import DerivedMetricsCreate, DerivedMetricsUpdate, DerivedMetricsResponse
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


@router.get("/", tags=["Derived Metrics"])
def get_derived_metrics(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'derived_metrics', 'read')
        metrics = db.query(models.DerivedMetrics).all()
        return {"count": len(metrics), "derived_metrics": [DerivedMetricsResponse.from_orm(m).dict() for m in metrics]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get derived metrics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch derived metrics")
    finally:
        db.close()


@router.get("/observation/{observation_id}", tags=["Derived Metrics"])
def get_observation_metrics(observation_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'derived_metrics', 'read')
        metrics = db.query(models.DerivedMetrics).filter_by(observation_id=observation_id).all()
        return {"observation_id": observation_id, "count": len(metrics),
                "derived_metrics": [DerivedMetricsResponse.from_orm(m).dict() for m in metrics]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get observation metrics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch derived metrics")
    finally:
        db.close()


@router.get("/{metric_id}", tags=["Derived Metrics"])
def get_metric(metric_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'derived_metrics', 'read')
        metric = db.query(models.DerivedMetrics).filter_by(metric_id=metric_id).first()
        if not metric:
            raise HTTPException(status_code=404, detail="Metric not found")
        return DerivedMetricsResponse.from_orm(metric).dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get metric error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch metric")
    finally:
        db.close()


@router.post("/", status_code=201, tags=["Derived Metrics"])
def create_metric(metric_data: DerivedMetricsCreate, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'derived_metrics', 'create')
        observation = db.query(models.Observation).filter_by(observation_id=metric_data.observation_id).first()
        if not observation:
            raise HTTPException(status_code=404, detail="Observation not found")
        metric = models.DerivedMetrics(
            observation_id=metric_data.observation_id,
            ndvi=metric_data.ndvi,
            evi=metric_data.evi,
            soil_moisture=metric_data.soil_moisture,
            crop_health_score=metric_data.crop_health_score,
        )
        db.add(metric)
        db.commit()
        db.refresh(metric)
        return {"message": "Derived metric created", "metric": DerivedMetricsResponse.from_orm(metric).dict()}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Create metric error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create metric")
    finally:
        db.close()


@router.put("/{metric_id}", tags=["Derived Metrics"])
def update_metric(metric_id: int, metric_data: DerivedMetricsUpdate, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'derived_metrics', 'update')
        metric = db.query(models.DerivedMetrics).filter_by(metric_id=metric_id).first()
        if not metric:
            raise HTTPException(status_code=404, detail="Metric not found")
        for field_name, value in metric_data.dict(exclude_none=True).items():
            setattr(metric, field_name, value)
        db.commit()
        db.refresh(metric)
        return {"message": "Metric updated", "metric": DerivedMetricsResponse.from_orm(metric).dict()}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Update metric error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update metric")
    finally:
        db.close()


@router.delete("/{metric_id}", tags=["Derived Metrics"])
def delete_metric(metric_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'derived_metrics', 'delete')
        metric = db.query(models.DerivedMetrics).filter_by(metric_id=metric_id).first()
        if not metric:
            raise HTTPException(status_code=404, detail="Metric not found")
        db.delete(metric)
        db.commit()
        return {"message": "Metric deleted"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Delete metric error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete metric")
    finally:
        db.close()