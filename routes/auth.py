from fastapi import APIRouter,HTTPException
from auth import AuthService
from schemas import UserCreate,UserLogin,UserResponse
import logging
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel

class Credentials(BaseModel):
    credentials: str

logger=logging.getLogger(__name__)
router=APIRouter()

@router.post("/register",status_code=201,tags=['Authentication'])
def register(user_data:UserCreate):
    result,status_code=AuthService.register(user_data)
    if status_code==201:
        user=result['user']
        return{"message":"user registered successfully","user":UserResponse.from_orm(user).dict()},201
    return result,status_code

@router.post("/login",tags=['Authentication'])
def login(login_data:UserLogin):
    result,status_code=AuthService.login(login_data.email,login_data.password)
    if status_code==200:
        user=result['user']
        return {
            "access_token": result['access_token'],
            "token_type": "Bearer",
            "user": UserResponse.from_orm(user).dict()
        }, 200
    return result,status_code
@router.get("/test", tags=["Authentication"])
def test():
    return {
        "message": "Auth routes working!",
        "endpoints": {
            "register": "POST /api/auth/register",
            "login": "POST /api/auth/login",
            "test": "GET /api/auth/test"
        }
    }
    
