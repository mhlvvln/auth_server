from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from auth.models import User
from auth.schemas import UserCreate, UserInfo
from auth.service import get_user, create_user, verify_password, create_access_token, get_current_user, get_user_admin
from database.database import get_db

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@auth_router.post("/register", summary="Регистрация")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, email=user.email)
    if db_user:
        return JSONResponse({"status": False, "error": "email уже занят"}, status_code=401)
    user = create_user(db=db, user=user)
    access_token = create_access_token(data={"sub": user.id, "email": user.email, "role": user.role},
                                       expires_delta=access_token_expires)
    return {"status": True, "id": str(user.id), "email": user.email, "role": user.role, "access_token": access_token,
            "token_type": "bearer"}


@auth_router.post("/token", summary="Логин для юзеров")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    email = form_data.username
    password = form_data.password

    db_user = get_user(db, email=email)
    if not db_user or not verify_password(password, db_user.password):
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Incorrect email or password",
        #     headers={"WWW-Authenticate": "Bearer"},
        # )
        return JSONResponse({"status": False, "error": "Неверный логин или пароль"}, status_code=401,
                            headers={"WWW-Authenticate": "Bearer"})

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": db_user.id, "email": db_user.email, "role": db_user.role},
                                       expires_delta=access_token_expires)

    return {"status": True, "access_token": access_token, "token_type": "bearer", "id": db_user.id}


@auth_router.post("/a_token", summary="Логин для админов")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    верные данные:<br>
    логин - mhlvvln@gmail.com<br>
    пароль - password
    """
    email = form_data.username
    password = form_data.password

    db_user = get_user_admin(db, email=email)
    if not db_user or not verify_password(password, db_user.password):
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Incorrect email or password",
        #     headers={"WWW-Authenticate": "Bearer"},
        # )
        return JSONResponse({"status": False, "error": "Неверный логин или пароль"}, status_code=401,
                            headers={"WWW-Authenticate": "Bearer"})

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": db_user.id, "email": db_user.email, "role": db_user.role},
                                       expires_delta=access_token_expires)

    return {"status": True, "access_token": access_token, "token_type": "bearer", "id": db_user.id}


@auth_router.get("/users/me", summary="Получить нынешнего пользователя")
def read_current_user(current_user: User = Depends(get_current_user)):
    try:
        return {"status": True, "user": UserInfo(
            id=current_user.id,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            email=current_user.email,
            role=current_user.role
        )}
    except:
        return JSONResponse({"status": False, "error": "неверный токен"})
