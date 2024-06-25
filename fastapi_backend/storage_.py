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
from functools import lru_cache
from typing import Optional, Union, AsyncGenerator


class FileSystemHandler:

    # 基本文件操作方法

    @lru_cache(maxsize=128)
    def get_path_basename(self, path: str, *args: str, **kargs: str) -> str:
        if path:
            return os.path.basename(path)
        else:
            logger.error("Path is empty")
            return ""

    @lru_cache(maxsize=128)
    def get_join_path(self, *paths: Union[str, Path], **kargs: str) -> str:
        joined_path = Path(*paths)
        return joined_path.as_posix()

    @lru_cache(maxsize=128)
    def get_path_dirname(self, path: Union[str, Path], *args: str, **kargs: str) -> str:
        return str(Path(path).parent)

    def makedirs(
        self, path: Union[str, Path], isfile: bool = True, *args: str, **kargs: str
    ):
        """
        will create a system path or directory if not exists.
        """
        path = Path(path)
        if not os.path.exists(path):
            pathd = path.parent if isfile else path
            pathd.mkdir(parents=True, exist_ok=True)

    @lru_cache(maxsize=128)
    def get_files_in_sys_dir_one_layer(
        self, path: str, extension: Optional[str] = None, *args: str, **kargs: str
    ):
        """
        path is a system directory

        if extension is None, return all files in the directory, just as os.listdir.only contain basename.

        if extension is not None, return all files with the extension in the directory.will contain relative file path.contain dir/filebasename.\
        
        """
        assert os.path.exists(path), f"Path not found: {path}"

        assert os.path.isdir(path), f"Path is not a directory: {path}"

        if extension:
            pathp = Path(path)
            ts_files = list(pathp.glob(f"*.{extension}"))

            ts_files2 = [
                Path(pathp, file.name).as_posix() for file in ts_files if file.is_file()
            ]

            assert len(ts_files) == len(
                ts_files2
            ), f"Error in get_files_in_sys_dir_one_layer: {ts_files} -> {ts_files2}"

            return ts_files2
        else:
            return os.listdir(path)

    # 以下方法由子类基础实现 , 函数签名保持一致 ，实现存储的抽象和解耦

    def is_file_exist(self, path: str, *args, **kwargs) -> bool:
        raise NotImplementedError

    def remove_file(self, path: str, *args, **kwargs) -> None:
        raise NotImplementedError

    def get_file_size(self, path: str, *args, **kwargs) -> int:
        raise NotImplementedError

    async def async_write_file_wb(
        self, path: str, content: bytes, *args, **kwargs
    ) -> None:
        raise NotImplementedError

    async def async_read_file_rb(self, path: str, *args, **kwargs) -> bytes:
        raise NotImplementedError

    def remove_path(self, path: str, *args, **kwargs) -> None:
        raise NotImplementedError

    def save_file_from_system_path(
        self, path: str, save_path: str, delete_original: bool = True, *args, **kwargs
    ) -> None:
        """
        path is a file pathstring. will create the path if not exists in storage layer.
        """
        raise NotImplementedError

    def get_file_bytestream(self, path: str, *args, **kwargs) -> Optional[bytes]:
        raise NotImplementedError

    async def file_iterator(
        self,
        file_path: str,
        start: int,
        end: int,
        chunk_size: int = 1024 * 1024,
        *args,
        **kwargs,
    ) -> AsyncGenerator[bytes, None]:
        """
        async generator to read file in chunks
        """
        raise NotImplementedError

    def get_dir_files(self, path: str, *args, **kwargs):
        """

        path is directory or dirprefix

        will return all files in the directory, not just a filebasename.

        """
        raise NotImplementedError


class LocalFileSystemHandler(FileSystemHandler):

    def get_dir_files(self, path, *args, **kwargs):
        """

        path is system directory

        will return all files in the directory, not just a filebasename.

        """

        assert os.path.exists(path), f"Path not found: {path}"

        assert os.path.isdir(path), f"Path is not a directory: {path}"

        return [
            os.path.join(path, file)
            for file in os.listdir(path)
            if os.path.isfile(os.path.join(path, file))  # os.path.isfile
        ]

    def is_file_exist(self, path, *args, **kwargs):
        return os.path.exists(path) if path else False

    def remove_file(self, path, *args, **kargs):
        if path and path != "" and self.is_file_exist(path):
            os.remove(path)

    @lru_cache(maxsize=128)
    def get_file_size(self, path, *args, **kwargs):
        return os.path.getsize(path)

    async def async_write_file_wb(self, path, content: bytes, *args, **kwargs):
        """
        path is a system file path. will create the path if not exists
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if (
            self.is_file_exist(path)
            and self.get_file_size(path) == len(content)
            and content == await self.async_read_file_rb(path)
        ):
            return
        async with aiofiles.open(path, "wb") as buffer:
            await buffer.write(content)

    async def async_read_file_rb(self, path, *args, **kwargs):
        async with aiofiles.open(path, "rb") as f:
            return await f.read()

    def remove_path(self, path, *args, **kwargs):
        if self.is_file_exist(path):
            shutil.rmtree(path)

    def save_file_from_system_path(
        self, path, save_path, delete_original=True, *args, **kwargs
    ):
        if os.path.exists(path) and path != save_path:
            shutil.copy(path, save_path)
            if delete_original:
                if os.path.exists(path) and os.path.isfile(path):
                    os.remove(path)
            logger.debug(f"save_file_from_system_path: {path} -> {save_path}")

    @lru_cache(maxsize=128)
    def get_file_bytestream(self, path, *args, **kwargs):
        assert self.is_file_exist(path), f"File not found: {path}"
        with open(path, "rb") as f:
            return f.read()

    async def file_iterator(
        self, file_path, start, end, chunk_size=1024 * 1024, *args, **kwargs
    ):
        async with aiofiles.open(file_path, mode="rb") as f:
            await f.seek(start)
            current_position = start
            while current_position <= end:
                remaining_bytes = end - current_position + 1
                read_size = min(chunk_size, remaining_bytes)
                chunk = await f.read(read_size)
                if not chunk:
                    break
                current_position += len(chunk)
                yield chunk


class MinioFileSystemHandler(FileSystemHandler):
    def __init__(self, client: Minio, bucket_name: str):
        self.client: Minio = client
        self.bucket_name: str = bucket_name

    def get_dir_files(self, path, *args, **kwargs):
        try:
            objects = self.client.list_objects(
                self.bucket_name, prefix=path, recursive=True
            )
            return [obj.object_name for obj in objects if obj.is_dir == False]
        except S3Error as e:
            logger.error(f"Failed to get dir files for {path}: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to get dir files for {path}: {str(e)}")

    def is_file_exist(self, path, *args, **kwargs):
        try:
            self.client.stat_object(self.bucket_name, path)
            return True
        except S3Error:
            return False
        except Exception as e:
            logger.debug(f"Failed to check file existence for {path}: {str(e)}")
            return False

    def remove_file(self, path, *args, **kargs):
        try:
            self.client.remove_object(self.bucket_name, path)
        except S3Error as e:
            logger.error(f"Failed to remove file {path}: {str(e)}")

    @lru_cache(maxsize=128)
    def get_file_size(self, path, *args, **kwargs):
        try:
            stat = self.client.stat_object(self.bucket_name, path)
            return stat.size
        except S3Error as e:
            logger.error(f"Failed to get file size for {path}: {str(e)}")
            return 0

    async def async_write_file_wb(self, path, content: bytes, *args, **kwargs):
        """
        path is a pathstring. will create the path if not exists
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.client.put_object(
                self.bucket_name, path, io.BytesIO(content), len(content)
            ),
        )

    async def async_read_file_rb(self, path, *args, **kwargs):
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: self.client.get_object(self.bucket_name, path)
        )
        try:
            data = response.read()
            return data
        finally:
            response.close()

    def remove_path(self, path, *args, **kwargs):
        # MinIO 不支持递归删除🥲
        try:
            objects_to_delete = self.client.list_objects(
                self.bucket_name, prefix=path, recursive=True
            )
            for obj in objects_to_delete:
                self.client.remove_object(self.bucket_name, obj.object_name)
        except S3Error as e:
            logger.error(f"Failed to remove path {path}: {str(e)}")

    def save_file_from_system_path(
        self, path, save_path, delete_original=True, *args, **kwargs
    ):
        try:
            assert os.path.exists(path), f"Path not found: {path}"
            if self.is_file_exist(save_path):
                logger.debug(f"File already exists: {save_path}")
                return
            with open(path, "rb") as file_data:
                file_stat = os.stat(path)
                self.client.put_object(
                    self.bucket_name, save_path, file_data, file_stat.st_size
                )
                logger.debug(f"save_file_from_system_path: {path} -> {save_path}")
            if delete_original:
                if os.path.exists(path) and os.path.isfile(path):
                    os.remove(path)
            logger.debug(f"save_file_from_system_path: {path} -> {save_path}")
        except Exception as e:
            logger.error(
                f"Failed to save file from system path {path} to {save_path}: {str(e)}: {type(e)}"
            )

    @lru_cache(maxsize=128)
    def get_file_bytestream(self, path, *args, **kwargs):
        try:
            response = self.client.get_object(self.bucket_name, path)
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
        self, file_path, start, end, chunk_size=1024 * 1024, *args, **kwargs
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
                lambda: self.client.get_object(
                    self.bucket_name,
                    object_name,
                    request_headers={"Range": range_header},
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


class FileHandlerFactory:

    @staticmethod
    def create_handler(*args, **kwargs):
        if config.StorageConfig.STORE_TYPE == "local":
            return LocalFileSystemHandler()
        elif config.StorageConfig.STORE_TYPE == "minio":
            client: Minio = config.StorageConfig.MinioClient
            bucket_name: str = config.StorageConfig.MINIO_BUCKET
            found = client.bucket_exists(bucket_name)
            if not found:
                client.make_bucket(bucket_name)
                logger.warning(f"Created bucket: {bucket_name}")
            else:
                logger.debug(f"Bucket already exists: {bucket_name}")
            return MinioFileSystemHandler(client, bucket_name)
        else:
            logger.critical("Invalid STORE_TYPE value in config.py")
            raise ValueError("Invalid STORE_TYPE value in config.py")


handler = FileHandlerFactory.create_handler()
