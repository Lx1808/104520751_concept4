from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta
from ..core.config import settings
from .model import Token, UserCreate
from .utils import authenticate_user, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
from dbsetting import get_user, create_new_user, create_user, serialize_objectid
from ..core.database import users
from .utils import get_current_user
from bson import ObjectId

router = APIRouter()


@router.post("/register", response_model=Token)
def register(user: UserCreate):
    db_user = get_user(user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)

    # Validate role
    if user.roles not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'user' or 'admin'")

    new_user = create_user(user.username, hashed_password, user.first_name, user.last_name, user.roles)
    created_user = create_new_user(new_user)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": serialize_objectid(created_user['_id'])}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user['username'],
            "first_name": current_user['first_name'],
            "roles": current_user['roles']}


async def get_user_id_by_username(username: str):
    user = users.find_one({"username": username}, {"_id": 1})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return str(user["_id"])


@router.delete("/users/{username}")
async def remove_user(
        username: str,
        current_user: dict = Depends(get_current_user)
):
    if current_user['roles'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")

    if current_user['username'] == username:
        raise HTTPException(status_code=400, detail="Cannot remove your own account")

    user_id = await get_user_id_by_username(username)

    result = users.delete_one({"_id": ObjectId(user_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"User {username} successfully removed"}


@router.put("/users/{username}/role")
async def update_user_role(
        username: str,
        new_role: str,
        current_user: dict = Depends(get_current_user)
):
    if current_user['roles'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")

    if current_user['username'] == username:
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    if new_role not in ['user', 'admin']:
        raise HTTPException(status_code=400, detail="Invalid role")

    user_id = await get_user_id_by_username(username)

    result = users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"roles": new_role}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"User {username}'s role updated to {new_role}"}


@router.get("/users")
async def get_all_users(current_user: dict = Depends(get_current_user)):
    if current_user['roles'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")

    user_list = list(users.find({}, {"_id": 0, "username": 1, "roles": 1, "first_name": 1}))
    return user_list