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
from abc import ABC, abstractmethod

STORE_TYPE = config.StorageConfig.STORE_TYPE


class FileHandler(ABC):
    @abstractmethod
    def remove_file(self, path: str) -> None:
        pass

    @abstractmethod
    def is_file_exist(self, path: str) -> bool:
        pass

    @abstractmethod
    def get_file_size(self, path: str) -> int:
        pass

    @abstractmethod
    async def async_write_file_wb(self, path: str, content: bytes) -> None:
        pass

    @abstractmethod
    async def async_read_file_rb(self, path: str) -> bytes:
        pass

    @abstractmethod
    def remove_path(self, path: str) -> None:
        pass

    @abstractmethod
    def save_file_from_system_path(
        self, path: str, save_path: str, delete_original: bool = True
    ) -> None:
        pass

    @abstractmethod
    def get_file_bytestream(self, path: str) -> bytes:
        pass

    @abstractmethod
    async def file_iterator(
        self, file_path: str, start: int, end: int, chunk_size: int = 1024 * 1024
    ):
        pass


class LocalFileHandler(FileHandler):
    def remove_file(self, path: str) -> None:
        if self.is_file_exist(path):
            os.remove(path)

    def is_file_exist(self, path: str) -> bool:
        return Path(path).exists()

    @lru_cache(maxsize=128)
    def get_file_size(self, path: str) -> int:
        return os.path.getsize(path)

    async def async_write_file_wb(self, path: str, content: bytes) -> None:
        if (
            self.is_file_exist(path)
            and self.get_file_size(path) == len(content)
            and content == await self.async_read_file_rb(path)
        ):
            return
        async with aiofiles.open(path, "wb") as buffer:
            await buffer.write(content)

    async def async_read_file_rb(self, path: str) -> bytes:
        async with aiofiles.open(path, "rb") as f:
            return await f.read()

    def remove_path(self, path: str) -> None:
        if self.is_file_exist(path):
            shutil.rmtree(path)

    def save_file_from_system_path(
        self, path: str, save_path: str, delete_original: bool = True
    ) -> None:
        if os.path.exists(path) and path != save_path:
            shutil.copy(path, save_path)
            if delete_original and os.path.exists(path):
                os.remove(path)
            logger.debug(f"save_file_from_system_path: {path} -> {save_path}")

    @lru_cache(maxsize=128)
    def get_file_bytestream(self, path: str) -> bytes:
        assert self.is_file_exist(path), f"File not found: {path}"
        with open(path, "rb") as f:
            return f.read()

    async def file_iterator(
        self, file_path: str, start: int, end: int, chunk_size: int = 1024 * 1024
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


class MinioFileHandler(FileHandler):
    def __init__(self, client: Minio, bucket_name: str):
        self.client = client
        self.bucket_name = bucket_name

    def remove_file(self, path: str) -> None:
        try:
            self.client.remove_object(self.bucket_name, path)
        except S3Error as e:
            logger.error(f"Failed to remove file {path}: {str(e)}")

    def is_file_exist(self, path: str) -> bool:
        try:
            self.client.stat_object(self.bucket_name, path)
            return True
        except S3Error:
            return False
        except Exception as e:
            logger.debug(f"Failed to check file existence for {path}: {str(e)}")
            return False

    def get_file_size(self, path: str) -> int:
        try:
            stat = self.client.stat_object(self.bucket_name, path)
            return stat.size
        except S3Error as e:
            logger.error(f"Failed to get file size for {path}: {str(e)}")
            return 0

    async def async_write_file_wb(self, path: str, content: bytes) -> None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.client.put_object(
                self.bucket_name, path, io.BytesIO(content), len(content)
            ),
        )

    async def async_read_file_rb(self, path: str) -> bytes:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: self.client.get_object(self.bucket_name, path)
        )
        try:
            return response.read()
        finally:
            response.close()

    def remove_path(self, path: str) -> None:
        try:
            objects_to_delete = self.client.list_objects(
                self.bucket_name, prefix=path, recursive=True
            )
            for obj in objects_to_delete:
                self.client.remove_object(self.bucket_name, obj.object_name)
        except S3Error as e:
            logger.error(f"Failed to remove path {path}: {str(e)}")

    def save_file_from_system_path(
        self, path: str, save_path: str, delete_original: bool = True
    ) -> None:
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
            if delete_original and os.path.exists(path):
                os.remove(path)
        except Exception as e:
            logger.error(
                f"Failed to save file from system path {path} to {save_path}: {str(e)}: {type(e)}"
            )

    @lru_cache(maxsize=128)
    def get_file_bytestream(self, path: str) -> bytes:
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
        self, file_path: str, start: int, end: int, chunk_size: int = 1024 * 1024
    ):
        object_name = file_path
        current_position = start
        while current_position <= end:
            remaining_bytes = end - current_position + 1
            read_size = min(chunk_size, remaining_bytes)
            range_header = (
                f"bytes={current_position}-{current_position + read_size - 1}"
            )

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
    def get_file_handler(store_type: str) -> FileHandler:
        if store_type == "local":
            return LocalFileHandler()
        elif store_type == "minio":
            client: Minio = config.StorageConfig.MinioClient
            bucket_name: str = config.StorageConfig.MINIO_BUCKET
            return MinioFileHandler(client, bucket_name)
        else:
            logger.critical("Invalid STORE_TYPE value in config.py")
            raise ValueError("Invalid STORE_TYPE value in config.py")


# Example usage:
file_handler = FileHandlerFactory.get_file_handler(STORE_TYPE)

# Use the file_handler to call methods as needed
