# encoding: utf-8

import os
from .base import Config
from pathlib import Path


class UserConfig(Config):
    __current_workspace_dir: Path = Path(__file__).parent.parent
    __DEFAULT_PROFILE_IMAGE: Path = (
        Path(__current_workspace_dir) / Path("res") / Path("whysiki.jpg")
    )

    __DEFAULT_PROFILE_IMAGE.parent.mkdir(parents=True, exist_ok=True)

    assert os.path.exists(
        __DEFAULT_PROFILE_IMAGE
    ), f"Default profile image {__DEFAULT_PROFILE_IMAGE} not found. please put a default profile image in the static folder."

    DEFAULT_PROFILE_IMAGE: str = __DEFAULT_PROFILE_IMAGE.relative_to(
        __current_workspace_dir
    ).as_posix()

    # 头像最大大小
    PROFILE_IMAGE_MAX_FILE_SIZE: int = 1024 * 1024 * 3
