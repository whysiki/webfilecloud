# encoding: utf-8

from dotenv import load_dotenv
import os


# Configuration classes
class Config:
    # read .env
    load_dotenv()
    # read environment variables
    # the path to store uploaded files
    UPLOAD_PATH: str = os.getenv("UPLOAD_PATH")
    # jwt secret key
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    # jwt algorithm
    ALGORITHM: str = os.getenv("ALGORITHM")
    # jwt expire time
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    # ROOT user
    ROOT_USER: str = os.getenv("ROOT_USER")
    # ROOT password
    ROOT_PASSWORD: str = os.getenv("ROOT_PASSWORD")
    # database URL
    # dialect[+driver]://user:password@host/dbname
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    os.makedirs(UPLOAD_PATH, exist_ok=True)

    assert (
        UPLOAD_PATH
        and SECRET_KEY
        and ALGORITHM
        and ACCESS_TOKEN_EXPIRE_MINUTES
        and ROOT_USER
        and ROOT_PASSWORD
        and DATABASE_URL
        and isinstance(ACCESS_TOKEN_EXPIRE_MINUTES, int)
        and isinstance(ROOT_USER, str)
        and isinstance(ROOT_PASSWORD, str)
        and isinstance(DATABASE_URL, str)
        and isinstance(UPLOAD_PATH, str)
        and isinstance(SECRET_KEY, str)
        and isinstance(ALGORITHM, str)
        and os.path.exists(UPLOAD_PATH)
    ), "Some environment variables are missing, please check your .env file. if you don't have one, please run `python env.py` to generate it."
