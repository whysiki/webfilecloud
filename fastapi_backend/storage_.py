import os

# import config
import aiofiles
import shutil
from pathlib import Path


def remove_file(path, *args, **kargs):
    if path and path != "" and is_file_exist(path):
        os.remove(path)


def get_path_basename(path, *args, **kargs):

    return os.path.basename(path)


def get_join_path(*paths, **kargs):
    joined_path = Path(*paths)
    return joined_path.as_posix()


def is_file_exist(path, *args, **kargs):
    # return Path(path).exists() if path else False
    return os.path.exists(path) if path else False


def get_path_dirname(path, *args, **kargs):
    return str(Path(path).parent)


def makedirs(path, isfile: bool = True, *args, **kargs):
    path = Path(path)
    if not is_file_exist(path):
        pathd = path.parent if isfile else path
        pathd.mkdir(parents=True, exist_ok=True)


def get_file_size(path, *args, **kargs):

    return os.path.getsize(path)


async def async_write_file_wb(path, content: bytes, *args, **kargs) -> None:
    if (
        is_file_exist(path)
        and get_file_size(path) == len(content)
        and content == await async_read_file_rb(path)
    ):
        return
    async with aiofiles.open(path, "wb") as buffer:
        await buffer.write(content)


async def async_read_file_rb(path, *args, **kargs) -> bytes:

    async with aiofiles.open(path, "rb") as f:

        return await f.read()


def remove_path(path, *args, **kargs):
    if is_file_exist(path):
        shutil.rmtree(path)


def save_file_from_system_path(path, save_path, *args, **kargs):
    if os.path.exists(path):
        shutil.copy(path, save_path)
