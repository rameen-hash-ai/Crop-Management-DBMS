from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from database import SessionLocal
import models
from schemas import UserResponse, UserUpdate
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


@router.get("/", tags=["Users"])
def get_users(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'users', 'read')
        if user.role in ['admin', 'agronomist']:
            users = db.query(models.User).all()
        else:
            users = db.query(models.User).filter_by(user_id=user.user_id).all()  # ✅ fixed
        return {"count": len(users), "user_role": user.role, "users": [UserResponse.from_orm(u).dict() for u in users]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get users error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")
    finally:
        db.close()  # ✅ always closes


@router.get("/{user_id}", tags=["Users"])
def get_user(user_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'users', 'read')
        if user.role == 'farmer' and int(current_user) != user_id:
            raise HTTPException(status_code=403, detail="Cannot view other users")
        target_user = db.query(models.User).filter_by(user_id=user_id).first()  # ✅ fixed
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse.from_orm(target_user).dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user")
    finally:
        db.close()


@router.put("/{user_id}", tags=["Users"])
def update_user(user_id: int, user_data: UserUpdate, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'users', 'update')
        if user.role == 'farmer' and int(current_user) != user_id:
            raise HTTPException(status_code=403, detail="Cannot update other users")
        target_user = db.query(models.User).filter_by(user_id=user_id).first()  # ✅ fixed
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        if user_data.name:
            target_user.name = user_data.name
        if user_data.email:
            target_user.email = user_data.email
        db.commit()
        db.refresh(target_user)
        return UserResponse.from_orm(target_user).dict()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Update user error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user")
    finally:
        db.close()


@router.delete("/{user_id}", tags=["Users"])
def delete_user(user_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = RoleBasedAccessControl.check_permission(int(current_user), 'users', 'delete')
        if user.role == 'farmer' and int(current_user) != user_id:
            raise HTTPException(status_code=403, detail="Cannot delete other users")
        target_user = db.query(models.User).filter_by(user_id=user_id).first()  # ✅ fixed
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(target_user)
        db.commit()
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Delete user error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user")
    finally:
        db.close()