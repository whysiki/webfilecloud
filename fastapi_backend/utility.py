# import os
from functools import lru_cache
import subprocess
import config  # custom configuration class, which contains configuration items
from config.status import StatusConfig as status  # custom status code class
from loguru import logger
from fastapi import HTTPException
import io
from PIL import Image
from functools import wraps
from storage_ import handler as storage_  # 存储层的一些自定义封装函数
import tempfile
import os
import shutil
from pathlib import Path
from typing import Tuple, Any, Callable
from config.storage import (
    STORE_TYPE_LOCAL,
    # STORE_TYPE_MINIO,
)  # custom storage type constant
from minio import Minio, S3Error
import asyncio
import json
from config.status import StatusConfig as Status
from typing import List
import numpy


def get_new_path(path: str) -> str:
    def split_path(path: str) -> Tuple[str, str]:
        parts = path.rsplit(".", 1)
        return (parts[0], parts[1]) if len(parts) > 1 else (path, "")

    name, extension = split_path(path)

    def get_path_r(pathr: str, intn: int = 1) -> str:
        if storage_.is_file_exist(pathr):
            new_path = f"{name}({intn}).{extension}" if extension else f"{name}({intn})"
            return get_path_r(new_path, intn + 1)
        else:
            return pathr

    return get_path_r(path)


@lru_cache(maxsize=128)
def get_file_extension(filepath: str):
    """
    Returns:
        str: File extension. example: "jpg", "mp4", "pdf", "txt", etc.
    Raises:
        return "binary" if the file has no extension.
    """
    try:
        path_obj = Path(filepath)
        _, extension = os.path.splitext(path_obj.name)
        if not extension:
            return "binary"
        return extension.lstrip(".")
    except Exception as e:
        logger.warning(f"Error obtaining file suffix: {e}")
        return "binary"


@lru_cache(maxsize=128)
def get_media_type_from_file_path(file_path: str) -> str:
    MIME_TYPES = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".ogg": "video/ogg",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".pdf": "application/pdf",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".xls": "application/vnd.ms-excel",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".zip": "application/zip",
        ".gz": "application/gzip",
    }
    extension: str = "." + get_file_extension(file_path)
    return MIME_TYPES.get(extension, "application/octet-stream")


@lru_cache(maxsize=128)
def generate_thumbnail(file_path: str, size: Tuple[int, int] = (200, 200)) -> bytes:
    """
    Generates a thumbnail image from the given file path.

    Args:
        file_path (str): Path to the image file.
        size (tuple, optional): Size of the thumbnail (width, height). Defaults to (200, 200).

    Returns:
        bytes: Thumbnail image bytes.

    Rainse:
        HTTP_500_INTERNAL_SERVER_ERROR
    """
    try:
        image = Image.open(io.BytesIO(storage_.get_file_bytestream(file_path)))  # type: ignore
        image.thumbnail(size)  # type: ignore
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=image.format)  # type: ignore
        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()
    except Exception as e:
        logger.warning(f"Error generating thumbnail: {str(e)} {type(e)}")
        try:
            LOAD_ERROR_IMG = config.FileConfig.LOAD_ERROR_IMG
            storage_.save_file_from_system_path(
                LOAD_ERROR_IMG, LOAD_ERROR_IMG, delete_original=False
            )
            if storage_.is_file_exist(LOAD_ERROR_IMG):
                image = Image.open(  # type: ignore
                    io.BytesIO(storage_.get_file_bytestream(LOAD_ERROR_IMG))  # type: ignore
                )
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format=image.format)  # type: ignore
                img_byte_arr.seek(0)
                return img_byte_arr.getvalue()
            else:
                logger.warning(
                    "Failed to load the default error image ,will generate a white image"
                )
            white_image = Image.new(
                "RGB", (int(size[0] / 2), int(size[1] / 2)), (255, 255, 255)
            )
            img_byte_arr = io.BytesIO()
            white_image.save(img_byte_arr, format="JPEG")  # type: ignore
            img_byte_arr.seek(0)
            return img_byte_arr.getvalue()
        except Exception as e:
            logger.error(f"Error generating default thumbnail: {str(e)} {type(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error generating thumbnail",
            )


@lru_cache(maxsize=128)
def generate_preview_video(video_path: str, output_path: str):
    """
    Generates a preview video from the given video file path.

    Args:
        video_path (str): Input video file path.
        output_path (str): Output preview video file path.

    Returns:
        str: Output preview video file path.

    Raises:

        HTTP_500_INTERNAL_SERVER_ERROR. If an error occurs while generating the preview video.
    """
    try:
        assert storage_.is_file_exist(video_path), "The video path does not exist"
        with tempfile.NamedTemporaryFile(
            suffix=f".{get_file_extension(video_path)}",
            dir=config.FileConfig.PREVIEW_FILES_PATH,
            delete=False,
        ) as tmp_file:
            tmp_file_path = tmp_file.name
            logger.debug(f"Temporary file path: {tmp_file_path}")  # 🤣
            tmp_file.write(storage_.get_file_bytestream(video_path))  # type: ignore
            duration_command = [
                r"ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                f"{str(tmp_file_path)}",
            ]
            result = subprocess.run(duration_command, capture_output=True, text=True)
            original_duration = float(result.stdout.strip())
            logger.debug(f"Original video duration: {original_duration}秒")
            preview_duration = min(original_duration, 5.0)
            try:
                command = [
                    r"ffmpeg",
                    "-i",
                    f"{tmp_file_path}",  # 输入视频文件路径
                    "-t",
                    str(preview_duration),  # 截取视频的时长，最多为5秒
                    "-vf",
                    "scale=-1:360",  # 设置视频高度为360p，宽度按比例缩放
                    "-c:v",
                    "libx264",  # 使用H.264编解码器
                    "-crf",
                    "30",  # 设置CRF值，数值越小质量越好，文件越大
                    "-preset",
                    "ultrafast",
                    "-an",  # 去除音频
                    "-y",  # 覆盖已存在的输出文件
                    f"{output_path}",  # 输出视频文件路径
                ]
                subprocess.run(command, check=True)
            except:
                logger.warning("default video width ..")
                command = [
                    r"ffmpeg",
                    "-i",
                    f"{tmp_file_path}",  # 输入视频文件路径
                    "-t",
                    str(preview_duration),  # 截取视频的时长，最多为5秒
                    # "-vf",
                    # "scale=-1:360",  # 设置视频高度为360p，宽度按比例缩放
                    "-c:v",
                    "libx264",  # 使用H.264编解码器
                    "-crf",
                    "30",  # 设置CRF值，数值越小质量越好，文件越大
                    "-preset",
                    "ultrafast",
                    "-an",  # 去除音频
                    "-y",  # 覆盖已存在的输出文件
                    f"{output_path}",  # 输出视频文件路径
                ]
                subprocess.run(command, check=True)

            finally:

                tmp_file.close()

            storage_.save_file_from_system_path(output_path, output_path)

        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

        assert storage_.is_file_exist(output_path), "failed to save preview video"

        if config.StorageConfig.STORE_TYPE != STORE_TYPE_LOCAL:

            if os.path.exists(output_path):

                os.remove(output_path)

        return output_path

    except subprocess.CalledProcessError as e:
        logger.error(f"ffmpeg command failed with exit status {e.returncode}")
        logger.error(f"ffmpeg output: {e.output}")
        logger.error(f"ffmpeg error: {e.stderr}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating video preview",
        )
    except Exception as e:
        logger.error(f"Error generating video preview: {str(e)},type:{type(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating video preview",
        )


@lru_cache(maxsize=128)
def generate_hls_playlist(
    input_file: str,
    output_dir: str,
    playlist_name: str,
    file_id: str,
    segment_time: int = 10,
    # threshold_size_mb: int = 400,
):
    """
    input_file (str): 输入视频文件路径
    output_dir (str): 输出目录，用于保存生成的播放列表和 TS 段
    playlist_name (str): 生成的播放列表文件名
    segment_time (int): 每个 TS 段的持续时间（秒），默认为 10 秒

    raise:
        HTTP_404_NOT_FOUND if the input file is not found.
    """

    if not storage_.is_file_exist(input_file):

        logger.error(f"Enter the video file path {input_file} not found!")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Input file not found, Failed to generate HLS playlist",
        )

    storage_.makedirs(output_dir, isfile=False)

    output_path = storage_.get_join_path(output_dir, playlist_name)

    with tempfile.NamedTemporaryFile(
        suffix=f".{get_file_extension(input_file)}",
        delete=False,
        dir=config.FileConfig.M3U8_INDEX_PATH,
    ) as tmp_file:

        tmp_file_path = tmp_file.name
        logger.debug(
            f"temporary file path: {tmp_file_path}, The path to the m3u8 list is displayed ： {output_path}"
        )
        tmp_file.write(storage_.get_file_bytestream(input_file))  # type: ignore

        if storage_.get_file_size(input_file) != os.path.getsize(tmp_file_path):
            logger.error(
                "The size of the temporary file is different from the original file!"
            )
        ffmpeg_command = [
            "ffmpeg",
            "-i",
            f"{tmp_file_path}",  # 临时比特流文件路径
            "-c",
            "copy",  # 使用 copy 编解码器
            "-start_number",
            "0",
            "-hls_time",
            str(segment_time),
            "-hls_list_size",
            "0",
            "-hls_segment_filename",
            storage_.get_join_path(
                output_dir, f"{file_id}%d.ts"
            ),  # 设置 TS 段文件名格式
            "-f",
            "hls",
            f"{output_path}",
        ]

        try:

            subprocess.run(
                ffmpeg_command,
                check=True,
                # stdout=subprocess.DEVNULL,
                # stderr=subprocess.DEVNULL,
            )

            ts_files = storage_.get_files_in_sys_dir_one_layer(
                output_dir, extension="ts"
            )

            for file_path in ts_files:

                storage_.save_file_from_system_path(
                    file_path,
                    file_path,
                )

                assert storage_.is_file_exist(file_path), "Failed to save ts file"

            storage_.save_file_from_system_path(
                output_path,
                output_path,
            )

            assert storage_.is_file_exist(output_path), "Failed to save m3u8 index file"

            logger.success(f"HLS playlist and segments generated at {output_dir}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate HLS playlist: {str(e)}")

        except Exception as e:

            logger.error(f"Failed to generate HLS playlist: {type(e)} {str(e)}")

        finally:
            tmp_file.close()
    if os.path.exists(tmp_file_path):
        os.remove(tmp_file_path)
    if config.StorageConfig.STORE_TYPE == "minio":
        if output_dir and os.path.exists(output_dir):
            shutil.rmtree(output_dir, ignore_errors=True)


from typing import Dict


def get_start_end_from_range_header(
    range_header: str,  # example: "bytes=0-1023"
    file_size: int,
    headers: Dict[str, str] = dict(),  # range_header = request.headers.get("Range")
) -> tuple[int, int]:
    """
    Calculates the start and end positions from the given range header.

    Args:
        range_header (str): The range header string, e.g., "bytes=0-1023". priority over headers.
        file_size (int): The size of the file in bytes.
        headers (dict, optional): Additional headers. Defaults to None.

    Returns:
        tuple[int, int]: A tuple containing the start and end positions.

    Raises:

        HTTP_400_BAD_REQUEST: If the file is not found or the range header is invalid.

        HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE: If the requested range is not satisfiable.
    """
    if headers and headers.get("Range"):
        range_header = headers["Range"]
    if not file_size:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    if range_header:
        try:
            start, end = range_header.replace("bytes=", "").split("-")
            start = int(start)
            end = int(end) if end else file_size - 1
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Range header"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Range header:{str(e)}",
            )
    else:
        start = 0
        end = file_size - 1

    if start >= file_size or end >= file_size:
        raise HTTPException(
            status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            detail="Requested Range Not Satisfiable",
        )

    return start, end


def require_double_confirmation(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    require_double_confirmation: A decorator that requires the user to confirm the action twice.

    Raises:
        HTTP_400_BAD_REQUEST: If the action is not confirmed.
    """
    confirmation_required: bool = False

    @wraps(func)
    async def wrapper(*args: Tuple[Any], **kwargs: dict[str, Any]):
        nonlocal confirmation_required
        if not confirmation_required:
            confirmation_required = True
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please confirm the action again",
            )
        result: Any = await func(*args, **kwargs)
        confirmation_required = False
        return result

    return wrapper


def store_type_specific(store_type: str):

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:

        async def wrapper(*args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> Any:

            if config.StorageConfig.STORE_TYPE == store_type:
                return await func(*args, **kwargs)
            else:
                logger.error(
                    f"Unsupported storage type on this endpoint, expected {store_type}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported storage type on this endpoint, expected {store_type}",
                )

        return wrapper

    return decorator


### minio
async def minio_file_iterator(
    client: Minio,
    bucket_name: str,
    object_name: str,
    start: int,
    end: int,
    chunk_size: int = 1024 * 1024,
):
    current_position = start
    while current_position <= end:
        remaining_bytes = end - current_position + 1
        read_size = min(chunk_size, remaining_bytes)
        range_header = f"bytes={current_position}-{current_position + read_size - 1}"

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


### minio
def minio_get_file_size(
    client: Minio,
    bucket_name: str,
    object_name: str,
    *args: Tuple[Any],
    **kwargs: dict[str, Any],
) -> int:
    try:
        stat = client.stat_object(bucket_name, object_name)
        return stat.size if stat.size else 0
    except S3Error as err:
        logger.error(f"Error getting size for {object_name}: {err}")
        return 0


def get_file_nodes(file_nodes: str | None) -> None:

    file_nodes_list: List[str] = []

    if file_nodes:

        file_nodes_list = json.loads(file_nodes)

        if len(numpy.array(file_nodes_list).shape) != 1:
            logger.error(f"invalid upload nodes: {file_nodes_list}")
            raise HTTPException(
                status_code=Status.HTTP_400_BAD_REQUEST, detail="invalid nodes"
            )
        if file_nodes_list:
            for node in file_nodes_list:
                if not node.strip():
                    logger.warning(
                        "The head of File nodes is empty, please input a valid node name. default: []"
                    )
                    file_nodes_list = []
                    break
        else:
            logger.warning(
                "The head of File nodes is empty, please input a valid node name. default: []"
            )
            file_nodes_list = []
    else:
        logger.warning(
            "The head of File nodes is empty, please input a valid node name. default: []"
        )
        file_nodes_list = []

    return file_nodes_list
