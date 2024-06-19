import os
from functools import lru_cache
import subprocess
import config
from loguru import logger
from fastapi import HTTPException
import io
from PIL import Image
# import imageio

# import ffmpeg

def get_new_path(path: str):
    name, extension = path.split(".")[-2],path.split(".")[-1] if len(path.split(".")) > 1 else [path, '']
    def get_path_r(pathr: str, intn: int = 1):
        if os.path.exists(pathr):
            return get_path_r(f"{name}({intn}).{extension}" if extension else f"{name}({intn})", intn + 1)
        else:
            return pathr
    return get_path_r(path)

# print(get_new_path(r"D:\xraytest\filecloud\fastapi_backend\test\test_1.py"))
            


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