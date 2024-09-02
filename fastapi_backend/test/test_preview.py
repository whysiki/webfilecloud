# import subprocess
# import os
# encoding: utf-8
from fastapi import HTTPException, Depends
from uuid import uuid4
from starlette.requests import Request
from sqlalchemy.orm import Session
import models  # 模型定义
import schemas
import crud  # 数据库操作
from auth import pwd_context, create_access_token, get_current_username
from fastapi import File, UploadFile
from datetime import datetime
import os
import shutil
from fastapi import Header
from typing import Optional
import auth  # 认证
from fastapi.responses import FileResponse
import hashlib
import config  # 自定义配置类，里面有配置项
from fastapi.responses import StreamingResponse
from io import BytesIO
import aiofiles
from loguru import logger
from dep import get_db  # 依赖注入
from app import app  # 应用实例
import json
import numpy
import utility
from pathlib import Path
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import io
import asyncio
import subprocess
from urllib.parse import quote
import imageio

# from concurrent.futures import ThreadPoolExecutor
from PIL import UnidentifiedImageError
import mimetypes
import ffmpeg

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


# 示例用法
video_path = r"uploads\whysiki\mp4\12.14 ジェーナス&ジャーヴィスSEX.mp4"
output_path = "preview.mp4"

generate_preview_video(video_path, output_path)


# # ## 视频预览
# # @app.get("/files/video/preview")
# # async def preview_video_file(
# #     file_id: str,
# #     Authorization: Optional[str] = Header(None),
# #     db: Session = Depends(get_db),
# # ):

# #     access_token = auth.get_access_token_from_Authorization(Authorization)
# #     username: str = get_current_username(access_token)
# #     user = crud.get_user_by_username(db, username)
# #     file = crud.get_file_by_id(db, file_id=file_id)

# #     if file.file_owner_name != user.username:
# #         raise HTTPException(status_code=403, detail="Permission denied")

# #     if not crud.is_fileid_in_user_files(db, user, file.id):
# #         raise HTTPException(
# #             status_code=404, detail="File not found in user's file list"
# #         )

# #     loop = asyncio.get_running_loop()
# #     with ThreadPoolExecutor(max_workers=4) as executor:
# #         preview_data = await loop.run_in_executor(
# #             executor, generate_video_preview, file.file_path
# #         )
# #     mime_type = "video/mp4"

# #     return StreamingResponse(
# #         io.BytesIO(preview_data),
# #         media_type=mime_type,
# #         headers={
# #             "Content-Disposition": f"attachment; filename=preview_{os.path.basename(file.file_path)}.mp4"
# #         },
# #     )
