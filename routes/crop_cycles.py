from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from database import SessionLocal
import models
from schemas import CropCycleCreate, CropCycleUpdate, CropCycleResponse
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


@router.get("/", tags=["Crop Cycles"])
def get_crop_cycles(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'crop_cycles', 'read')
        if user.role == 'farmer':
            cycles = db.query(models.CropCycle).join(models.Field).filter(
                models.Field.user_id == user.user_id  # ✅ user.user_id not user.id
            ).all()
            visibility = "own field cycles only"
        else:
            cycles = db.query(models.CropCycle).all()
            visibility = "all cycles"
        return {"count": len(cycles), "user_role": user.role, "visibility": visibility,
                "crop_cycles": [CropCycleResponse.from_orm(c).dict() for c in cycles]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get crop cycles error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch crop cycles")
    finally:
        db.close()


@router.get("/active/all", tags=["Crop Cycles"])  # ✅ moved ABOVE /{cycle_id} to avoid route conflict
def get_active_cycles(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'crop_cycles', 'read')
        if user.role == 'farmer':
            cycles = db.query(models.CropCycle).join(models.Field).filter(
                models.Field.user_id == user.user_id,  # ✅ fixed
                models.CropCycle.status == 'active'
            ).all()
        else:
            cycles = db.query(models.CropCycle).filter_by(status='active').all()
        return {"count": len(cycles), "status": "active",
                "crop_cycles": [CropCycleResponse.from_orm(c).dict() for c in cycles]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get active cycles error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch active cycles")
    finally:
        db.close()


@router.get("/field/{field_id}", tags=["Crop Cycles"])
def get_field_cycles(field_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'crop_cycles', 'read')
        field = db.query(models.Field).filter_by(field_id=field_id).first()  # ✅ field_id not id
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        if user.role == 'farmer' and field.user_id != user.user_id:  # ✅ fixed
            raise HTTPException(status_code=403, detail="Access denied")
        cycles = db.query(models.CropCycle).filter_by(field_id=field_id).all()
        return {"field_id": field_id, "count": len(cycles),
                "crop_cycles": [CropCycleResponse.from_orm(c).dict() for c in cycles]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get field cycles error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch field cycles")
    finally:
        db.close()


@router.get("/{cycle_id}", tags=["Crop Cycles"])
def get_crop_cycle(cycle_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'crop_cycles', 'read')
        cycle = db.query(models.CropCycle).filter_by(cycle_id=cycle_id).first()  # ✅ cycle_id not id
        if not cycle:
            raise HTTPException(status_code=404, detail="Crop cycle not found")
        if user.role == 'farmer':
            field = db.query(models.Field).filter_by(field_id=cycle.field_id, user_id=user.user_id).first()  # ✅ fixed
            if not field:
                raise HTTPException(status_code=403, detail="Access denied")
        return CropCycleResponse.from_orm(cycle).dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get crop cycle error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch crop cycle")
    finally:
        db.close()


@router.post("/", status_code=201, tags=["Crop Cycles"])
def create_crop_cycle(cycle_data: CropCycleCreate, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'crop_cycles', 'create')
        field = db.query(models.Field).filter_by(field_id=cycle_data.field_id).first()  # ✅ fixed
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        if user.role == 'farmer' and field.user_id != user.user_id:  # ✅ fixed
            raise HTTPException(status_code=403, detail="Cannot create cycle for others' field")
        cycle = models.CropCycle(
            field_id=cycle_data.field_id,
            crop_name=cycle_data.crop_name,
            start_date=str(cycle_data.start_date),
            expected_harvest_date=str(cycle_data.expected_harvest_date),
        )
        db.add(cycle)
        db.commit()
        db.refresh(cycle)
        return {"message": "Crop cycle created", "cycle": CropCycleResponse.from_orm(cycle).dict()}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Create crop cycle error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create crop cycle")
    finally:
        db.close()


@router.put("/{cycle_id}", tags=["Crop Cycles"])
def update_crop_cycle(cycle_id: int, cycle_data: CropCycleUpdate, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'crop_cycles', 'update')
        cycle = db.query(models.CropCycle).filter_by(cycle_id=cycle_id).first()  # ✅ fixed
        if not cycle:
            raise HTTPException(status_code=404, detail="Crop cycle not found")
        if user.role == 'farmer':
            field = db.query(models.Field).filter_by(field_id=cycle.field_id, user_id=user.user_id).first()  # ✅ fixed
            if not field:
                raise HTTPException(status_code=403, detail="Cannot update others' cycles")
        if cycle_data.crop_name:
            cycle.crop_name = cycle_data.crop_name
        if cycle_data.status:
            cycle.status = cycle_data.status
        if cycle_data.actual_harvest_date:
            cycle.actual_harvest_date = str(cycle_data.actual_harvest_date)
        if cycle_data.expected_harvest_date:
            cycle.expected_harvest_date = str(cycle_data.expected_harvest_date)
        db.commit()
        db.refresh(cycle)
        return {"message": "Crop cycle updated", "cycle": CropCycleResponse.from_orm(cycle).dict()}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Update crop cycle error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update crop cycle")
    finally:
        db.close()


@router.delete("/{cycle_id}", tags=["Crop Cycles"])
def delete_crop_cycle(cycle_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'crop_cycles', 'delete')
        if user.role == 'agronomist':  # ✅ moved up before DB query
            raise HTTPException(status_code=403, detail="Agronomists cannot delete cycles")
        cycle = db.query(models.CropCycle).filter_by(cycle_id=cycle_id).first()  # ✅ fixed
        if not cycle:
            raise HTTPException(status_code=404, detail="Crop cycle not found")
        if user.role == 'farmer':
            field = db.query(models.Field).filter_by(field_id=cycle.field_id, user_id=user.user_id).first()  # ✅ fixed
            if not field:
                raise HTTPException(status_code=403, detail="Cannot delete others' cycles")
        db.delete(cycle)
        db.commit()
        return {"message": "Crop cycle deleted"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Delete crop cycle error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete crop cycle")
    finally:
        db.close()