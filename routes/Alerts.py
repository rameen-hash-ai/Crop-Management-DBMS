from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from database import SessionLocal
import models
from schemas import AlertCreate, AlertUpdate, AlertResponse
from auth import RoleBasedAccessControl
import logging
import os
from datetime import datetime

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


@router.get("/", tags=["Alerts"])
def get_alerts(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'alerts', 'read')
        if user.role == 'farmer':
            alerts = db.query(models.Alert).join(models.Field).filter(
                models.Field.user_id == user.user_id
            ).all()
        else:
            alerts = db.query(models.Alert).all()
        return {"count": len(alerts), "alerts": [AlertResponse.from_orm(a).dict() for a in alerts]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get alerts error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")
    finally:
        db.close()


@router.get("/unresolved", tags=["Alerts"])  # ✅ before /{alert_id} to avoid route conflict
def get_unresolved_alerts(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'alerts', 'read')
        if user.role == 'farmer':
            alerts = db.query(models.Alert).join(models.Field).filter(
                models.Field.user_id == user.user_id,
                models.Alert.is_resolved == False
            ).all()
        else:
            alerts = db.query(models.Alert).filter_by(is_resolved=False).all()
        return {"count": len(alerts), "alerts": [AlertResponse.from_orm(a).dict() for a in alerts]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get unresolved alerts error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")
    finally:
        db.close()


@router.get("/{alert_id}", tags=["Alerts"])
def get_alert(alert_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'alerts', 'read')
        alert = db.query(models.Alert).filter_by(alert_id=alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        if user.role == 'farmer':
            field = db.query(models.Field).filter_by(field_id=alert.field_id, user_id=user.user_id).first()
            if not field:
                raise HTTPException(status_code=403, detail="Access denied")
        return AlertResponse.from_orm(alert).dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get alert error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch alert")
    finally:
        db.close()


@router.post("/", status_code=201, tags=["Alerts"])
def create_alert(alert_data: AlertCreate, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'alerts', 'create')
        field = db.query(models.Field).filter_by(field_id=alert_data.field_id).first()
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        alert = models.Alert(
            field_id=alert_data.field_id,
            observation_id=alert_data.observation_id,
            alert_type=alert_data.alert_type,
            severity=alert_data.severity,
            message=alert_data.message,
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return {"message": "Alert created", "alert": AlertResponse.from_orm(alert).dict()}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Create alert error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create alert")
    finally:
        db.close()


@router.put("/{alert_id}", tags=["Alerts"])
def update_alert(alert_id: int, alert_data: AlertUpdate, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'alerts', 'update')
        alert = db.query(models.Alert).filter_by(alert_id=alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        for field_name, value in alert_data.dict(exclude_none=True).items():
            setattr(alert, field_name, value)
        if alert_data.is_resolved and not alert.resolved_at:
            alert.resolved_at = datetime.utcnow()
        db.commit()
        db.refresh(alert)
        return {"message": "Alert updated", "alert": AlertResponse.from_orm(alert).dict()}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Update alert error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update alert")
    finally:
        db.close()


@router.delete("/{alert_id}", tags=["Alerts"])
def delete_alert(alert_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        RoleBasedAccessControl.check_permission(int(current_user), 'alerts', 'delete')
        alert = db.query(models.Alert).filter_by(alert_id=alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        db.delete(alert)
        db.commit()
        return {"message": "Alert deleted"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Delete alert error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete alert")
    finally:
        db.close()