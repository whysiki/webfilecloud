import os
from functools import lru_cache
import subprocess
import config
from loguru import logger
from fastapi import HTTPException
import io
from PIL import Image
import aiofiles

# import imageio

# import ffmpeg


def get_new_path(path: str):
    name, extension = path.split(".")[-2], (
        path.split(".")[-1] if len(path.split(".")) > 1 else [path, ""]
    )

    def get_path_r(pathr: str, intn: int = 1):
        if os.path.exists(pathr):
            return get_path_r(
                f"{name}({intn}).{extension}" if extension else f"{name}({intn})",
                intn + 1,
            )
        else:
            return pathr

    return get_path_r(path)


# print(get_new_path(r"D:\xraytest\filecloud\fastapi_backend\test\test_1.py"))


async def file_iterator(file_path: str, start: int, end: int):
    async with aiofiles.open(file_path, mode="rb") as f:
        await f.seek(start)
        chunk_size = 1024 * 1024
        current_position = start
        while current_position <= end:  # 只要当前位置小于等于end，就继续读取。 包含end
            remaining_bytes = (
                end - current_position + 1
            )  # 从当前位置读到 end , 闭区间，一共有的字节数
            read_size = min(chunk_size, remaining_bytes)  # 不超过chunk_size
            chunk = await f.read(read_size)  # 读取
            if not chunk:  # 到达文件末尾
                break
            current_position += len(chunk)  # 移动位置
            yield chunk


@lru_cache(maxsize=256)
def generate_thumbnail(file_path: str, size: tuple = (200, 200)) -> bytes:
    try:
        with Image.open(file_path) as image:
            image.thumbnail(size)
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format=image.format)
            img_byte_arr.seek(0)
            return img_byte_arr.getvalue()
    except Exception as e:
        LOAD_ERROR_IMG = config.File.LOAD_ERROR_IMG
        if os.path.exists(LOAD_ERROR_IMG):
            with Image.open(LOAD_ERROR_IMG) as image:
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
        assert os.path.exists(video_path), "视频路径不存在"
        # 获取原视频的时长
        duration_command = [
            r"ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            f"{str(video_path)}",
        ]
        result = subprocess.run(duration_command, capture_output=True, text=True)
        original_duration = float(result.stdout.strip())

        print(f"原视频时长: {original_duration}秒")

        # 确定裁剪的时长（最多5秒）
        preview_duration = min(original_duration, 5.0)

        try:

            # 构建ffmpeg命令
            command = [
                r"ffmpeg",
                "-i",
                f"{video_path}",  # 输入视频文件路径
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
                f"{video_path}",  # 输入视频文件路径
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

    if not os.path.exists(input_file):

        logger.error(f"{input_file} not found!")

        raise ValueError(f"{input_file} not found!")

    if not os.path.exists(output_dir):

        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, playlist_name)

    ffmpeg_command = [
        "ffmpeg",
        "-i",
        f"{input_file}",
        "-c",
        "copy",  # 使用 copy 编解码器
        "-start_number",
        "0",
        "-hls_time",
        str(segment_time),
        "-hls_list_size",
        "0",
        "-hls_segment_filename",
        os.path.join(output_dir, f"{file_id}%d.ts"),  # 设置 TS 段文件名格式
        "-f",
        "hls",
        f"{output_path}",
    ]

    # try:
    #     subprocess.run(ffmpeg_command, check=True)
    #     logger.info(f"HLS playlist and segments generated at {output_dir}")
    # except subprocess.CalledProcessError as e:
    #     logger.error(f"Failed to generate HLS playlist: {e}")

    try:
        subprocess.run(
            ffmpeg_command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logger.info(f"HLS playlist and segments generated at {output_dir}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to generate HLS playlist: {e}")
