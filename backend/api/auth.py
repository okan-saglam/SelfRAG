from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import EmailStr
from backend.models.user import UserCreate, UserLogin, UserOut, UserInDB
from backend.utils.auth import hash_password, verify_password, create_access_token, decode_token
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/auth", tags=["auth"])

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "selfRAG")
client = AsyncIOMotorClient(MONGODB_URI)
db = client[DB_NAME]
users_collection = db["users"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    username = payload.get("sub")
    user = await users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/register", response_model=UserOut)
async def register(user: UserCreate):
    if await users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    if await users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed = hash_password(user.password)
    user_dict = user.dict()
    user_dict["hashed_password"] = hashed
    user_dict.pop("password")
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()
    user_dict["is_active"] = True
    user_dict["is_admin"] = False
    await users_collection.insert_one(user_dict)
    return UserOut(**{k: user_dict[k] for k in UserOut.__fields__ if k in user_dict})

@router.post("/login")
async def login(credentials: UserLogin):
    user = await users_collection.find_one({"username": credentials.username})
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user["username"]})
    refresh_token = create_access_token({"sub": user["username"]}, expires_delta=timedelta(days=7))
    await users_collection.update_one({"username": user["username"]}, {"$set": {"last_login": datetime.utcnow()}})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {k: user[k] for k in UserOut.__fields__ if k in user}
    }

@router.get("/me", response_model=UserOut)
async def get_me(current_user=Depends(get_current_user)):
    return UserOut(**{k: current_user[k] for k in UserOut.__fields__ if k in current_user})

@router.put("/me", response_model=UserOut)
async def update_me(updates: dict, current_user=Depends(get_current_user)):
    allowed = {"email", "full_name"}
    update_data = {k: v for k, v in updates.items() if k in allowed}
    update_data["updated_at"] = datetime.utcnow()
    await users_collection.update_one({"username": current_user["username"]}, {"$set": update_data})
    user = await users_collection.find_one({"username": current_user["username"]})
    return UserOut(**{k: user[k] for k in UserOut.__fields__ if k in user})

@router.post("/refresh")
async def refresh_token(request: Request):
    data = await request.json()
    token = data.get("refresh_token")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    username = payload.get("sub")
    user = await users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    access_token = create_access_token({"sub": username})
    refresh_token = create_access_token({"sub": username}, expires_delta=timedelta(days=7))
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {k: user[k] for k in UserOut.__fields__ if k in user}
    } 