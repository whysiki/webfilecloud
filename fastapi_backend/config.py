# encoding: utf-8

from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


# Configuration classes
class Config:
    # Read environment variables
    UPLOAD_PATH: str = os.getenv("UPLOAD_PATH", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    ROOT_USER: str = os.getenv("ROOT_USER", "")
    ROOT_PASSWORD: str = os.getenv("ROOT_PASSWORD", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    STATIC_PATH: str = "static"

    # Validate environment variables
    assert UPLOAD_PATH, "UPLOAD_PATH is missing, please check your .env file."
    assert SECRET_KEY, "SECRET_KEY is missing, please check your .env file."
    assert ALGORITHM, "ALGORITHM is missing, please check your .env file."
    assert (
        ACCESS_TOKEN_EXPIRE_MINUTES > 0
    ), "ACCESS_TOKEN_EXPIRE_MINUTES is missing or invalid, please check your .env file."
    assert ROOT_USER, "ROOT_USER is missing, please check your .env file."
    assert ROOT_PASSWORD, "ROOT_PASSWORD is missing, please check your .env file."
    assert DATABASE_URL, "DATABASE_URL is missing, please check your .env file."

    os.makedirs(UPLOAD_PATH, exist_ok=True)
    os.makedirs(STATIC_PATH, exist_ok=True)

    assert os.path.exists(UPLOAD_PATH), "Upload path not found."
    assert os.path.exists(STATIC_PATH), "Static path not found."

    # CORS origins
    CROS_ORIGINS: list = ["*"]

    # GZIP response minimum size
    GZIP_MINIMUM_SIZE: int = 500


class User(Config):
    # Default profile image path
    DEFAULT_PROFILE_IMAGE: str = os.path.join("whysiki.jpg")

    assert os.path.exists(DEFAULT_PROFILE_IMAGE), "Default profile image not found."

    # 头像最大大小
    PROFILE_IMAGE_MAX_FILE_SIZE: int = 1024 * 1024 * 3


class File(Config):

    LOAD_ERROR_IMG = "whysiki_load_error.jpg"

    assert os.path.exists(LOAD_ERROR_IMG), "Load error image not found."
    
    PREVIEW_FILES_PATH: str = os.path.join("cache","preview")
