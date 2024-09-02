# encoding: utf-8

import os
from .base import Config
from pathlib import Path


class FileConfig(Config):

    __current_workspace_dir: Path = Path(__file__).parent.parent

    __LOAD_ERROR_IMG: Path = (
        Path(__file__).parent.parent / Path("res") / Path("whysiki_load_error.jpg")
    )
    assert os.path.exists(__LOAD_ERROR_IMG), "Load error image not found."
    __PREVIEW_FILES_PATH = (
        Path(__file__).parent.parent / Path("cache") / Path("preview")
    )
    __M3U8_INDEX_PATH = Path(__file__).parent.parent / Path("cache") / Path("m3u8")
    os.makedirs(__PREVIEW_FILES_PATH, exist_ok=True)
    os.makedirs(__M3U8_INDEX_PATH, exist_ok=True)

    LOAD_ERROR_IMG: str = __LOAD_ERROR_IMG.relative_to(
        __current_workspace_dir
    ).as_posix()
    PREVIEW_FILES_PATH: str = __PREVIEW_FILES_PATH.relative_to(
        __current_workspace_dir
    ).as_posix()
    M3U8_INDEX_PATH: str = __M3U8_INDEX_PATH.relative_to(
        __current_workspace_dir
    ).as_posix()
