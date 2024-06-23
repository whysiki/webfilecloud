import os
import config
import aiofiles
import shutil
from pathlib import Path
from loguru import logger
import asyncio
from minio import Minio
from minio.error import S3Error
import io

STORE_TYPE = config.Config.STORE_TYPE

# basic file operations


def get_path_basename(path, *args, **kargs):
    """
    get the file name from the path
    """

    return os.path.basename(path)


def get_join_path(*paths, **kargs):
    """
    get the joined path from the paths
    """
    joined_path = Path(*paths)
    return joined_path.as_posix()


def get_path_dirname(path, *args, **kargs):
    """
    get the directory name from the path
    """

    return str(Path(path).parent)


def get_files_in_sys_dir_one_layer(path, extension=None, *args, **kargs):
    """

    dir is a system path.

    will contain relatave path of files, not just a file name

    extension: str, file extension to filter files . example: 'ts'

    path: str, path to directory

    return: list of files in the directory.

    """
    assert os.path.exists(path), f"Path not found: {path}"

    assert os.path.isdir(path), f"Path is not a directory: {path}"

    if extension:
        path = Path(path)
        ts_files = list(path.glob(f"*.{extension}"))

        return ts_files
    else:
        return os.listdir(path)


def makedirs(path, isfile: bool = True, *args, **kargs):
    path = Path(path)
    if not is_file_exist(path):
        pathd = path.parent if isfile else path
        pathd.mkdir(parents=True, exist_ok=True)


def remove_file(path, *args, **kwargs):
    pass


def is_file_exist(path, *args, **kwargs):
    pass


def get_file_size(path, *args, **kwargs):
    pass


async def async_write_file_wb(path, content: bytes, *args, **kwargs):
    pass


async def async_read_file_rb(path, *args, **kwargs):
    pass


def remove_path(path, *args, **kwargs):
    pass


def save_file_from_system_path(path, save_path, delete_original=True, *args, **kwargs):
    pass


def get_file_bytestream(path, *args, **kwargs):
    pass


async def file_iterator(file_path, start, end, chunk_size=1024 * 1024, *args, **kwargs):
    pass


if STORE_TYPE == "local":

    def remove_file(path, *args, **kargs):
        if path and path != "" and is_file_exist(path):
            os.remove(path)

    def is_file_exist(path, *args, **kargs):
        return os.path.exists(path) if path else False

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

    def save_file_from_system_path(
        path, save_path, delete_original=True, *args, **kargs
    ):

        if os.path.exists(path) and path != save_path:
            shutil.copy(path, save_path)
            if delete_original:
                if os.path.exists(path) and os.path.isfile(path):
                    os.remove(path)
        logger.debug(f"save_file_from_system_path: {path} -> {save_path}")

    def get_file_bytestream(path, *args, **kargs):
        assert is_file_exist(path), f"File not found: {path}"
        with open(path, "rb") as f:
            return f.read()

    async def file_iterator(
        file_path: str,
        start: int,
        end: int,
        chunk_size: int = 1024 * 1024,
        *args,
        **kargs,
    ):
        async with aiofiles.open(file_path, mode="rb") as f:
            await f.seek(start)
            chunk_size = 1024 * 1024
            current_position = start
            while (
                current_position <= end
            ):  # 只要当前位置小于等于end，就继续读取。 包含end
                remaining_bytes = (
                    end - current_position + 1
                )  # 从当前位置读到 end , 闭区间，一共有的字节数
                read_size = min(chunk_size, remaining_bytes)  # 不超过chunk_size
                chunk = await f.read(read_size)  # 读取
                if not chunk:  # 到达文件末尾
                    break
                current_position += len(chunk)  # 移动位置
                yield chunk

elif STORE_TYPE == "minio":

    client: Minio = config.Config.MinioClient
    bucket_name: str = config.Config.MINIO_BUCKET

    found = client.bucket_exists(bucket_name)
    if not found:
        client.make_bucket(bucket_name)
        logger.warning(f"Created bucket: {bucket_name}")
    else:
        logger.debug(f"Bucket already exists: {bucket_name}")

    def remove_file(path, *args, **kargs):
        try:
            client.remove_object(bucket_name, path)
        except S3Error as e:
            logger.error(f"Failed to remove file {path}: {str(e)}")

    def is_file_exist(path, *args, **kargs):
        try:
            client.stat_object(bucket_name, path)
            return True
        except S3Error:
            return False
        except Exception as e:
            logger.error(f"Failed to check file existence for {path}: {str(e)}")
            return False

    def get_file_size(path, *args, **kargs):
        try:
            stat = client.stat_object(bucket_name, path)
            return stat.size
        except S3Error as e:
            logger.error(f"Failed to get file size for {path}: {str(e)}")
            return 0

    async def async_write_file_wb(path, content: bytes, *args, **kargs) -> None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: client.put_object(
                bucket_name, path, io.BytesIO(content), len(content)
            ),
        )

    async def async_read_file_rb(path, *args, **kargs) -> bytes:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: client.get_object(bucket_name, path)
        )
        try:
            data = response.read()
            return data
        finally:
            response.close()

    def remove_path(path, *args, **kargs):
        # MinIO 不支持递归删除🥲
        try:
            objects_to_delete = client.list_objects(
                bucket_name, prefix=path, recursive=True
            )
            for obj in objects_to_delete:
                client.remove_object(bucket_name, obj.object_name)
        except S3Error as e:
            logger.error(f"Failed to remove path {path}: {str(e)}")

    def save_file_from_system_path(
        path, save_path, delete_original=True, *args, **kargs
    ):
        try:
            assert os.path.exists(path), f"Path not found: {path}"
            with open(path, "rb") as file_data:
                file_stat = os.stat(path)
                client.put_object(bucket_name, save_path, file_data, file_stat.st_size)
            if delete_original:
                if os.path.exists(path) and os.path.isfile(path):
                    os.remove(path)
            logger.debug(f"save_file_from_system_path: {path} -> {save_path}")
        except Exception as e:
            logger.error(
                f"Failed to save file from system path {path} to {save_path}: {str(e)}"
            )

    def get_file_bytestream(path, *args, **kargs):
        try:
            response = client.get_object(bucket_name, path)
            try:
                return response.read()
            finally:
                response.close()
        except S3Error as e:
            logger.error(f"File not found: {path}")
            raise FileNotFoundError(f"File not found: {path}")
        except Exception as e:
            logger.error(
                f"Failed to get file bytestream for {path}: {str(e)} {type(e)}"
            )
            raise FileNotFoundError(f"File not found: {path}")

    async def file_iterator(
        file_path: str,
        start: int,
        end: int,
        chunk_size: int = 1024 * 1024,
        *args,
        **kargs,
    ):
        object_name = file_path
        current_position = start
        while current_position <= end:
            remaining_bytes = end - current_position + 1
            read_size = min(chunk_size, remaining_bytes)
            range_header = (
                f"bytes={current_position}-{current_position + read_size - 1}"
            )

            print(range_header)

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.get_object(
                    bucket_name, object_name, request_headers={"Range": range_header}
                ),
            )

            try:
                with response as stream:
                    while True:
                        chunk = stream.read(chunk_size)
                        if not chunk:
                            break
                        current_position += len(chunk)
                        yield chunk
            finally:
                response.close()

else:

    logger.critical("Invalid STORE_TYPE value in config.py")
    raise ValueError("Invalid STORE_TYPE value in config.py")
