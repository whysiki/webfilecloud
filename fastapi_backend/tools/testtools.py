# import asyncio
import httpx

# import json
# from rich import print
from rich.console import Console

# from rich.prompt import Prompt
import functools

# from dotenv import load_dotenv
import os

# import aiofiles
# from uuid import uuid4
# from pathlib import Path
from PIL import Image
import cv2

# import config
import random

# import shutil
# import re
# from tqdm import tqdm
# from httpx import AsyncClient
# from urllib.parse import unquote
import numpy as np


console = Console()


def handle_error(func):
    @functools.wraps(func)
    async def wrapp(*args, **kwargs):
        error = None
        for i in range(3):
            try:
                return await func(*args, **kwargs)
            except httpx.HTTPStatusError as e:
                error = e
                console.print(f"HTTP error occurred: {type(e)}:{str(e)}", style="red")
            except httpx.RequestError as e:
                error = e
                console.print(
                    f"Request error occurred: {type(e)}:{str(e)}", style="red"
                )
            except httpx.ReadTimeout as e:
                error = e
                console.print(f"Read timeout: {type(e)}:{str(e)}", style="red")
            except Exception as e:
                error = e
                console.print(
                    f"An unexpected error occurred: {type(e)}:{str(e)}", style="red"
                )

            console.print(f"attempt time {i+1}/4", style="yellow")

        raise error

    return wrapp


def generate_random_image(width, height, mode="RGB") -> Image:
    # 创建一个新的空白图片
    image = Image.new(mode, (width, height))
    pixels = image.load()
    if mode == "RGB":

        for x in range(width):
            for y in range(height):
                # 生成随机颜色
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                pixels[x, y] = (r, g, b)
    # 如果是灰度图
    elif mode == "L":
        for x in range(width):
            for y in range(height):
                # 生成随机颜色
                gray = random.randint(0, 255)
                pixels[x, y] = gray
    # 纯色图片
    elif mode == "1":
        color = 1
        for x in range(width):
            for y in range(height):
                pixels[x, y] = color
    return image


def get_new_path(path: str) -> str:
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


def generate_random_frame(width, height):
    # 生成随机颜色帧
    frame = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    return frame


def generate_random_video(width, height, num_frames, fps, output_path):
    # 使用 VideoWriter 创建视频写入对象
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # 使用MP4V编解码器
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for _ in range(num_frames):
        frame = generate_random_frame(width, height)
        out.write(frame)

    out.release()
