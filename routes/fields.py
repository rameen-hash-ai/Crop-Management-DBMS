from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from database import SessionLocal
import models
from schemas import FieldCreate, FieldUpdate, FieldResponse
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


@router.get("/", tags=["Fields"])
def get_fields(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'fields', 'read')
        if user.role == 'farmer':
            fields = db.query(models.Field).filter_by(user_id=user.user_id).all()  # ✅ user.user_id not user.id
            visibility = "own fields only"
        else:
            fields = db.query(models.Field).all()
            visibility = "all fields"
        return {"count": len(fields), "user_role": user.role, "visibility": visibility,
                "fields": [FieldResponse.from_orm(f).dict() for f in fields]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get fields error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch fields")
    finally:
        db.close()


@router.get("/{field_id}", tags=["Fields"])
def get_field(field_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'fields', 'read')
        field = db.query(models.Field).filter_by(field_id=field_id).first()  # ✅ field_id not id
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        if user.role == 'farmer' and field.user_id != user.user_id:  # ✅ user.user_id not user.id
            raise HTTPException(status_code=403, detail="Access denied")
        return FieldResponse.from_orm(field).dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get field error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch field")
    finally:
        db.close()


@router.post("/", status_code=201, tags=["Fields"])
def create_field(field_data: FieldCreate, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'fields', 'create')
        if user.role == 'farmer' and field_data.user_id != user.user_id:  # ✅ user.user_id not user.id
            raise HTTPException(status_code=403, detail="Cannot create field for others")
        field = models.Field(
            # ✅ removed field_id — let DB autoincrement it
            user_id=field_data.user_id,
            region_id=field_data.region_id,
            latitude=field_data.latitude,
            longitude=field_data.longitude,
            area=field_data.area,
            soil_type=field_data.soil_type,
        )
        db.add(field)
        db.commit()
        db.refresh(field)
        return {"message": "Field created", "field": FieldResponse.from_orm(field).dict()}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Create field error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create field")
    finally:
        db.close()


@router.put("/{field_id}", tags=["Fields"])
def update_field(field_id: int, field_data: FieldUpdate, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'fields', 'update')
        field = db.query(models.Field).filter_by(field_id=field_id).first()  # ✅ fixed
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        if user.role == 'farmer' and field.user_id != user.user_id:  # ✅ fixed
            raise HTTPException(status_code=403, detail="Cannot update others' fields")
        if field_data.soil_type:
            field.soil_type = field_data.soil_type
        if field_data.area:
            field.area = field_data.area
        if field_data.latitude:
            field.latitude = field_data.latitude
        if field_data.longitude:
            field.longitude = field_data.longitude
        db.commit()
        db.refresh(field)
        return {"message": "Field updated", "field": FieldResponse.from_orm(field).dict()}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Update field error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update field")
    finally:
        db.close()


@router.delete("/{field_id}", tags=["Fields"])
def delete_field(field_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'fields', 'delete')
        if user.role == 'agronomist':  # ✅ moved up before DB query — no point querying if role blocks it
            raise HTTPException(status_code=403, detail="Agronomists cannot delete fields")
        field = db.query(models.Field).filter_by(field_id=field_id).first()  # ✅ fixed
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        if user.role == 'farmer' and field.user_id != user.user_id:  # ✅ fixed
            raise HTTPException(status_code=403, detail="Cannot delete others' fields")
        db.delete(field)
        db.commit()
        return {"message": "Field deleted"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Delete field error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete field")
    finally:
        db.close()