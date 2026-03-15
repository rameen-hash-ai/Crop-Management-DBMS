from flask_jwt_extended import create_access_token
from datetime import timedelta
from database import SessionLocal
import models
from schemas import UserCreate,UserLogin
from fastapi import HTTPException,status
import logging
import bcrypt

logger=logging.getLogger(__name__)

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
    def check_permission(user_id,resource,action):
        db=SessionLocal()
        try:
            user=db.query(models.User).filter_by(id=user_id).first() #search in the user table and find the first id that matches the user_id
            if not user:
                raise HTTPException(status_code=404,detail=f"User Not found")
            if user.role not in ROLE_PERMISSIONS:
                raise HTTPException(status_code=403,detail=f'Unknown User {user.role}')
            user_perms=ROLE_PERMISSIONS[user.role] 

            if resource not in user_perms: #resource is the entity we are trying to acess
                raise HTTPException(status_code=403,detail=f'Access to {resource} not allowed')
            
            if action not in user_perms[resource]:
                raise HTTPException(status_code=403,detail=f"cannot{action} the {resource}")
            logger.info(f"User {user.email} ({user.role} authorized for {action} on {resource})")
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authorization error: {str(e)}")
            raise HTTPException(status_code=500,detail="Authorization check failed")
        finally:
            db.close()

    @staticmethod
    def is_admin(user_id):
        db=SessionLocal()
        try:
            user=db.query(models.User) .filter_by(id=user_id).first()
            return user and user.role=="admin"
        finally:
            db.close()

    @staticmethod
    def is_agronomist(user_id):
        db=SessionLocal()
        try:
            user=db.query(models.User).filter_by(id=user_id).first()
            return user and user.role=="agronomist"
        finally:
            db.close
    def is_farmer(user_id):
        db=SessionLocal()
        try:
            user=db.query(models.User).filter_by(id=user_id).first()
            return user and user.role=="farmer"
        finally:
            db.close()
class AuthService:
    @staticmethod
    def hash_passoword(password:str):
        salt=bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"),salt).decode('utf-8')
    @staticmethod
    def verify_password(password,hashed_password):
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode("utf-8"))
    @staticmethod
    def register(user_data:UserCreate):
        db=SessionLocal()
        try:
            existing_user=db.query(models.User).filter_by(email=user_data.email).first()
            if existing_user:
                raise HTTPException(status_code=409,detail=f"user email {user_data} already registered")
            valid_roles=["farmer","agronomist","admin"]
            if user_data.role not in valid_roles:
                raise HTTPException(status_code=400,detail=f"Invalid role")
            user=models.User(
                name=user_data.name,
                email=user_data.email,
                role=user_data.role,
                is_active=True
            
            )
            user.password_hash=AuthService.hash_passoword(user_data.password)

            db.add(user)
            db.commit()
            db.refresh(user)

            logger.info(f"user registered {user.name} role: {user.role}")
            return {'user':user}, 201
        except Exception as e:
            db.rollback()
            logger.error(f'Registration error {str(e)}')
            return {'error':"Registration failed"},400
        finally:
            db.close()
    @staticmethod
    def login(email:str,password:str):
        db=SessionLocal()
        try:
            user=db.query(models.User).filter_by(email=email).first()
            if not user:
                raise HTTPException(status_code=401,details="Invalid credentials")
            if not user.is_active:
                raise HTTPException(status_code=403,details='Account disabled')
            if not AuthService.verify_password(password,user.password_hash):
                raise HTTPException(status_code=401,details='Invalid password')
            access_token=create_access_token(
                identify=str(user.id),
                additional_claims={"role":user.role},
                expires_delta=timedelta(hours=24)
            )
            logger.info(f"User logged in {email} role: {user.role}")
            return {"access-token":access_token,"user":user},200
        except Exception as e:
            logger.error(f"Login error {str(e)}")
            return {"error":"Login failed"},400
        finally:
            db.close()