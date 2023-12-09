import os
from datetime import timedelta, datetime
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from auth import schemas
from .models import User as UserModel
from database.database import SessionLocal, get_db
from passlib.context import CryptContext
from .schemas import TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    to_encode["sub"] = str(to_encode["sub"])
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24 * 7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # credentials_exception = HTTPException(
    #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     detail={""},
    #     headers={"WWW-Authenticate": "Bearer"},
    # )
    try:
        print("hello")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = str(payload.get("sub"))
        role: str = payload.get("role")
        if id is None:
            return JSONResponse({"status": False, "error": "не авторизован"}, status_code=401)
        token_data = payload.get("email")
    except JWTError as e:
        return JSONResponse({"status": False, "error": str(e)}, status_code=401)
    user = get_user(db, email=token_data)
    if user is None:
        return JSONResponse({"status": False, "error": "не авторизован"}, status_code=401)
    return user


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: Session, email: str):
    return (db.query(UserModel)
            .filter(UserModel.email == email,
                    UserModel.disabled == False,
                    UserModel.role != "admin")
            .first())


def get_user_admin(db: Session, email: str):
    return db.query(UserModel).filter(UserModel.email == email).filter(UserModel.role == 'admin').first()


def create_user(db: Session, user: schemas.UserCreate):
    pass
    db_user = UserModel(**user.model_dump())
    db_user.password = get_password_hash(db_user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# if __name__ == "__main__":
#     session = SessionLocal()
#
#     user_create = schemas.UserCreate(first_name="aald", last_name="mdamd", email="masdha@gmail.com",
#                                      password="asdasd", role="user")
#
#     create_user(session, user_create)
