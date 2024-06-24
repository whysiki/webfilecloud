# encoding: utf-8

from dotenv import load_dotenv
from minio import Minio

# from minio.error import S3Error
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

    os.makedirs(STATIC_PATH, exist_ok=True)

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

    # CORS origins
    CROS_ORIGINS: list[str] = ["*"]

    # GZIP response minimum size
    GZIP_MINIMUM_SIZE: int = 500

    # storage

    STORE_TYPE: str = os.getenv("STORE_TYPE", "local").strip().lower()

    assert STORE_TYPE in [
        "local",
        "minio",
    ], "STORE_TYPE is invalid, please check your .env file. accepted values are 'local' or 'minio'."

    if STORE_TYPE == "minio":

        MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "")

        MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "")

        MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "")

        assert MINIO_ENDPOINT, "MINIO_ENDPOINT is missing, please check your .env file."
        assert (
            MINIO_ACCESS_KEY
        ), "MINIO_ACCESS_KEY is missing, please check your .env file."

        assert (
            MINIO_SECRET_KEY
        ), "MINIO_SECRET_KEY is missing, please check your .env file."

        MINIO_SECURE = os.getenv("MINIO_SECURE", "True")

        assert MINIO_SECURE in [
            "True",
            "False",
        ], "MINIO_SECURE is invalid, please check your .env file. accepted values are 'True' or 'False'."

        MinioClient = Minio(
            endpoint=MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=True if MINIO_SECURE == "True" else False,
        )

        MINIO_BUCKET = os.getenv("MINIO_BUCKET", "")

        assert MINIO_BUCKET, "MINIO_BUCKET is missing, please check your .env file."

        # 分片上传临时目录
        TEMP_UPLOAD_DIR = "temp_upload_dir"


class User(Config):
    # Default profile image path
    DEFAULT_PROFILE_IMAGE: str = os.path.join("whysiki.jpg")

    assert os.path.exists(DEFAULT_PROFILE_IMAGE), "Default profile image not found."

    # 头像最大大小
    PROFILE_IMAGE_MAX_FILE_SIZE: int = 1024 * 1024 * 3


class File(Config):

    LOAD_ERROR_IMG = "whysiki_load_error.jpg"

    assert os.path.exists(LOAD_ERROR_IMG), "Load error image not found."

    # assert os.path.exists(LOAD_ERROR_IMG), "Load error image not found."

    # PREVIEW_FILES_PATH: str = os.path.join("cache", "preview")

    # M3U8_INDEX_PATH: str = os.path.join("cache", "m3u8")

    PREVIEW_FILES_PATH: str = os.path.join("cache")
    M3U8_INDEX_PATH: str = os.path.join("cache")

    os.makedirs(PREVIEW_FILES_PATH, exist_ok=True)
    os.makedirs(M3U8_INDEX_PATH, exist_ok=True)

    # os.makedirs(M3U8_INDEX_PATH, exist_ok=True)

    # os.makedirs(PREVIEW_FILES_PATH, exist_ok=True)
