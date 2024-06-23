# import os
from functools import lru_cache
import subprocess
import config
from loguru import logger
from fastapi import HTTPException
import io
from PIL import Image
from functools import wraps
import storage_
import tempfile
import os

# import os
from pathlib import Path


def get_new_path(path: str):
    name, extension = path.split(".")[-2], (
        path.split(".")[-1] if len(path.split(".")) > 1 else [path, ""]
    )

    def get_path_r(pathr: str, intn: int = 1):
        if storage_.is_file_exist(pathr):
            return get_path_r(
                f"{name}({intn}).{extension}" if extension else f"{name}({intn})",
                intn + 1,
            )
        else:
            return pathr

    return get_path_r(path)


def get_file_extension(filepath):
    try:
        path_obj = Path(filepath)
        _, extension = os.path.splitext(path_obj.name)
        if not extension:
            return "binary"
        return extension.lstrip(".")
    except Exception as e:
        logger.warning(f"获取文件后缀时出错: {e}")
        return "binary"


@lru_cache(maxsize=256)
def generate_thumbnail(file_path: str, size: tuple = (200, 200)) -> bytes:
    try:
        image = Image.open(storage_.get_file_bytestream(file_path))
        image.thumbnail(size)
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=image.format)
        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()
    except Exception as e:
        LOAD_ERROR_IMG = config.File.LOAD_ERROR_IMG
        if storage_.is_file_exist(LOAD_ERROR_IMG):
            image = Image.open(storage_.get_file_bytestream(LOAD_ERROR_IMG))
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format=image.format)
            img_byte_arr.seek(0)
            return img_byte_arr.getvalue()
        white_image = Image.new("RGB", size, (255, 255, 255))
        img_byte_arr = io.BytesIO()
        white_image.save(img_byte_arr, format="JPEG")
        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()


@lru_cache(maxsize=128)
def generate_preview_video(video_path, output_path):
    try:
        assert storage_.is_file_exist(video_path), "视频路径不存在"
        with tempfile.NamedTemporaryFile(
            suffix=f".{get_file_extension(video_path)}",
            dir=config.File.PREVIEW_FILES_PATH,
            delete=False,
        ) as tmp_file:
            tmp_file_path = tmp_file.name
            logger.debug(f"临时文件路径: {tmp_file_path}")
            tmp_file.write(storage_.get_file_bytestream(video_path))
            # 获取原视频的时长
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

            logger.debug(f"原视频时长: {original_duration}秒")

            # 确定裁剪的时长（最多5秒）
            preview_duration = min(original_duration, 5.0)

            try:

                # 构建ffmpeg命令
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
                # 执行ffmpeg命令
                subprocess.run(command, check=True)
            except:

                logger.warning("default video width ..")

                # 构建ffmpeg命令
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
                # 执行ffmpeg命令
                subprocess.run(command, check=True)

            storage_.save_file_from_system_path(output_path, output_path)

        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"ffmpeg command failed with exit status {e.returncode}")
        logger.error(f"ffmpeg output: {e.output}")
        logger.error(f"ffmpeg error: {e.stderr}")
        raise HTTPException(status_code=500, detail="Error generating video preview")
    except Exception as e:
        logger.error(f"Error generating video preview: {e}")
        raise HTTPException(status_code=500, detail="Error generating video preview")


def generate_hls_playlist(
    input_file: str,
    output_dir: str,
    playlist_name: str,
    file_id: str,
    segment_time: int = 10,
):
    """
    input_file (str): 输入视频文件路径
    output_dir (str): 输出目录，用于保存生成的播放列表和 TS 段
    playlist_name (str): 生成的播放列表文件名
    segment_time (int): 每个 TS 段的持续时间（秒），默认为 10 秒
    """

    if not storage_.is_file_exist(input_file):

        logger.error(f"Enter the video file path {input_file} not found!")

        raise ValueError(f"{input_file} not found!")

    if not storage_.is_file_exist(output_dir):

        logger.warning(
            f"Output directory to hold the generated playlist and TS segment {output_dir} not found! ,will create dir"
        )

        storage_.makedirs(output_dir, isfile=False)

    output_path = storage_.get_join_path(output_dir, playlist_name)

    with tempfile.NamedTemporaryFile(
        suffix=f".{get_file_extension(input_file)}",
        delete=False,
        dir=config.File.M3U8_INDEX_PATH,
    ) as tmp_file:

        tmp_file_path = tmp_file.name
        logger.debug(
            f"emporary file path: {tmp_file_path}, The path to the m3u8 list is displayed ： {output_path}"
        )
        tmp_file.write(storage_.get_file_bytestream(input_file))

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

            # print(ffmpeg_command)
            subprocess.run(
                ffmpeg_command,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.info(f"HLS playlist and segments generated at {output_dir}")

            ts_files = storage_.get_files_in_sys_dir_one_layer(
                output_dir, extension="ts"
            )

            for file_path in ts_files:

                storage_.save_file_from_system_path(
                    file_path,
                    file_path,
                )

            storage_.save_file_from_system_path(
                output_path,
                output_path,
            )

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate HLS playlist: {e}")

        finally:
            # tmp_file.delete = True
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)


def get_start_end_from_range_header(
    range_header: str,  # example: "bytes=0-1023"
    file_size: int,
    headers: dict = None,  # range_header = request.headers.get("Range")
) -> tuple[int, int]:
    if headers and headers.get("Range"):
        range_header = headers.get("Range")
    if not file_size:
        raise HTTPException(status_code=404, detail="File not found")
    if range_header:
        try:
            start, end = range_header.replace("bytes=", "").split("-")
            start = int(start)
            end = int(end) if end else file_size - 1
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Range header")
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid Range header:{str(e)}"
            )
    else:
        start = 0
        end = file_size - 1

    if start >= file_size or end >= file_size:
        raise HTTPException(status_code=416, detail="Requested Range Not Satisfiable")

    return start, end


def require_double_confirmation(func):
    confirmation_required = False

    @wraps(func)
    async def wrapper(*args, **kwargs):
        nonlocal confirmation_required
        if not confirmation_required:
            confirmation_required = True
            raise HTTPException(
                status_code=400, detail="Please confirm the action again"
            )
        result = await func(*args, **kwargs)
        confirmation_required = False
        return result

    return wrapper


#  Failed to generate HLS playlist: Command
# '['ffmpeg', '-i', 'C:\\Users\\Administrator\\AppData\\Local\\Temp\\tmp7p_b1toy.mkv', '-c', 'copy', '-start_number', '0', '-hls_time', '10', '-hls_list_size', '0', '-hls_segment_filename', 'cache\\2ad84c30b057e07fac76bb0e78f391377bd4f79e72b8f6453d6d7520b483653ae47b7f69ffee819e2747bdc26025e8ee0ff56f5dda39a3ee5e6b4b0d3255bfef95601890afd80709\\1ff60b82-e884-41c1-a20e-0f41ba0f28b7%d.ts', '-f', 'hls', 'cache\\2ad84c30b057e07fac76bb0e78f391377bd4f79e72b8f6453d6d7520b483653ae47b7f69ffee819e2747bdc26025e8ee0ff56f5dda39a3ee5e6b4b0d3255bfef95601890afd80709\\index.m3u8']'
#  returned non-zero exit status 4294967283.


# ['ffmpeg', '-i', 'uploads/2ad84c30b057e07fac76bb0e78f391377bd4f79e72b8f6453d6d7520b483653a.mkv', '-c', 'copy', '-start_number', '0', '-hls_time', '10', '-hls_list_size', '0', '-hls_segment_filename', 'cache\\m3u8\\2ad84c30b057e07fac76bb0e78f391377bd4f79e72b8f6453d6d7520b483653ae47b7f69ffee819e2747bdc26025e8ee0ff56f5dda39a3ee5e6b4b0d3255bfef95601890afd80709\\2ad84c30b057e07fac76bb0e78f391377bd4f79e72b8f6453d6d7520b483653ae47b7f69ffee819e2747bdc26025e8ee0ff56f5dda39a3ee5e6b4b0d3255bfef95601890afd80709%d.ts', '-f', 'hls', 'cache\\m3u8\\2ad84c30b057e07fac76bb0e78f391377bd4f79e72b8f6453d6d7520b483653ae47b7f69ffee819e2747bdc26025e8ee0ff56f5dda39a3ee5e6b4b0d3255bfef95601890afd80709\\index.m3u8']
