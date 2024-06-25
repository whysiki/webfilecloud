# encoding: utf-8

import os
from minio import Minio
from .base import Config
from pathlib import Path


class StorageConfig(Config):

    __current_workspace_dir: Path = Path(__file__).parent.parent

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
    __TEMP_UPLOAD_DIR: Path = Path(__file__).parent.parent / Path("temp_upload_dir")

    os.makedirs(__TEMP_UPLOAD_DIR, exist_ok=True)

    TEMP_UPLOAD_DIR: str = __TEMP_UPLOAD_DIR.relative_to(
        __current_workspace_dir
    ).as_posix()
