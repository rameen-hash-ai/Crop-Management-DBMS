from jose import jwt
from datetime import timedelta,datetime
from database import SessionLocal
import models
from schemas import UserCreate,UserLogin
from fastapi import HTTPException,status
import logging
import bcrypt
import os
logger = logging.getLogger(__name__)
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"

def create_access_token(identity: str, additional_claims: dict, expires_delta: timedelta):
    payload = {"sub": identity, "exp": datetime.utcnow() + expires_delta, **additional_claims}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

ROLE_PERMISSIONS={
    'admin':{
        'users':['create','read','update','delete'],
        'regions':['create','read','update','delete'],
        'fields':['create','read','update','delete'],
        'crop_cycles':['create','read','update','delete'],
        'satellites':['create','read','update','delete'],
        'observations':['create','read','update','delete'],
        'band_values':['create','read','update','delete'],
        'weather':['create','read','update','delete'],
        'derived_metrics':['create','read','update','delete'],
        'alerts':['create','read','update','delete'], },
    'agronomist':{
        'users': ['read'],
        'regions': ['read'],
        'fields': ['read', 'update'],
        'crop_cycles': ['create', 'read', 'update'],
        'satellites': ['read'],
        'observations': ['read'],
        'band_values': ['read'],
        'weather': ['read'],
        'derived_metrics': ['read'],
        'alerts': ['create', 'read', 'update'],
    },

    'farmer':{
        'users': ['read'],
        'regions': ['read'],
        'fields': ['read', 'update'],
        'crop_cycles': ['read', 'update'],
        'satellites': ['read'],
        'observations': ['read'],
        'band_values': ['read'],
        'weather': ['read'],
        'derived_metrics': ['read'],
        'alerts': ['read'],
    }
}

class RoleBasedAccessControl:
    @staticmethod
    def check_permission(user_id, resource, action):
        db = SessionLocal()
        try:
            user = db.query(models.User).filter_by(user_id=user_id).first()  # ✅ fixed
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            if user.role not in ROLE_PERMISSIONS:
                raise HTTPException(status_code=403, detail=f"Unknown role: {user.role}")
            user_perms = ROLE_PERMISSIONS[user.role]
            if resource not in user_perms:
                raise HTTPException(status_code=403, detail=f"Access to {resource} not allowed")
            if action not in user_perms[resource]:
                raise HTTPException(status_code=403, detail=f"Cannot {action} on {resource}")
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authorization error: {str(e)}")
            raise HTTPException(status_code=500, detail="Authorization check failed")
        finally:
            db.close()

    @staticmethod
    def is_admin(user_id):
        db = SessionLocal()
        try:
            user = db.query(models.User).filter_by(user_id=user_id).first()  # ✅ fixed
            return user and user.role == "admin"
        finally:
            db.close()

    @staticmethod
    def is_agronomist(user_id):
        db = SessionLocal()
        try:
            user = db.query(models.User).filter_by(user_id=user_id).first()  # ✅ fixed
            return user and user.role == "agronomist"
        finally:
            db.close()  # ✅ fixed — was missing ()

    @staticmethod  # ✅ fixed — was missing decorator
    def is_farmer(user_id):
        db = SessionLocal()
        try:
            user = db.query(models.User).filter_by(user_id=user_id).first()  # ✅ fixed
            return user and user.role == "farmer"
        finally:
            db.close()

class AuthService:
    @staticmethod
    def hash_password(password: str):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def verify_password(password, hashed_password):
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    @staticmethod
    def register(user_data: UserCreate):
        db = SessionLocal()
        try:
            existing_user = db.query(models.User).filter_by(email=user_data.email).first()
            if existing_user:
                raise HTTPException(status_code=409, detail=f"Email {user_data.email} already registered")  # ✅ fixed
            valid_roles = ["farmer", "agronomist", "admin"]
            if user_data.role not in valid_roles:
                raise HTTPException(status_code=400, detail="Invalid role")
            user = models.User(
                name=user_data.name,
                email=user_data.email,
                role=user_data.role,
                is_active=True
            )
            user.password_hash = AuthService.hash_password(user_data.password)
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"User registered: {user.name}, role: {user.role}")
            return {"user": user}, 201
        except HTTPException:  # ✅ fixed — re-raise instead of swallowing
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Registration error: {str(e)}")
            raise HTTPException(status_code=400, detail="Registration failed")
        finally:
            db.close()

    @staticmethod
    def login(email: str, password: str):
        db = SessionLocal()
        try:
            user = db.query(models.User).filter_by(email=email).first()
            if not user:
                raise HTTPException(status_code=401, detail="Invalid credentials")  # ✅ fixed: detail not details
            if not user.is_active:
                raise HTTPException(status_code=403, detail="Account disabled")     # ✅ fixed
            if not AuthService.verify_password(password, user.password_hash):
                raise HTTPException(status_code=401, detail="Invalid credentials")  # ✅ fixed
            access_token = create_access_token(
                identity=str(user.user_id),
                additional_claims={"role": user.role},
                expires_delta=timedelta(hours=24)
            )
            logger.info(f"User logged in: {email}, role: {user.role}")
            return {"access_token": access_token, "user": user}, 200
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            raise HTTPException(status_code=400, detail="Login failed")
        finally:
            db.close()