# encoding: utf-8

from argon2 import PasswordHasher
import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException
from typing import Optional
from config.status import StatusConfig as status  # custom status codes
from config import Config  # 导入配置文件

# 使用 argon2-cffi 创建一个密码哈希器
pwd_context = PasswordHasher()


# 密码验证函数
def verify_password(plain_password: str, hashed_password: str):
    try:
        return pwd_context.verify(hashed_password, plain_password)
    except Exception:
        return False


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(
    data: dict[str, str], expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    expire = (
        datetime.utcnow() + expires_delta  # type: ignore
        if expires_delta
        else datetime.utcnow() + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)  # type: ignore
    )
    to_encode.update({"exp": expire})  # type: ignore
    encoded_jwt = jwt.encode(to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)
    return encoded_jwt


def get_current_username(token: str) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        username: str = payload.get("sub")
        now = datetime.utcnow()  # type: ignore
        if now > datetime.fromtimestamp(payload.get("exp")):
            raise credentials_exception
        if not username:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    return username


def get_access_token_from_Authorization(authorization: str) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ")[1]
    return token
