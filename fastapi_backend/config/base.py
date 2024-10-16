# encoding: utf-8

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
dislodged: bool = load_dotenv(
    verbose=True,
)

if not dislodged:

    dislodged: bool = load_dotenv(
        verbose=True,
        dotenv_path=Path(__file__).parent.parent / Path(".env"),
    )

if not dislodged:

    raise Exception(
        "Failed to load .env file, please check your environment variables."
    )


class Config:

    __current_workspace_dir: Path = Path(__file__).parent.parent

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

    __STATIC_PATH = Path(__file__).parent.parent / Path("static")

    os.makedirs(__STATIC_PATH, exist_ok=True)

    STATIC_PATH: str = __STATIC_PATH.relative_to(__current_workspace_dir).as_posix()

    # CORS origins
    CORS_ORIGINS: list[str] = ["*"]

    # GZIP response minimum size
    GZIP_MINIMUM_SIZE: int = 500

    VERIFY_TOKEN_IN_PREVIEW_VIDEO: bool = False

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
