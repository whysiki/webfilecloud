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


# 注册用户
@app.post("/users/register", response_model=schemas.UserOut)
async def register_user(user_in: schemas.UserIn, db: Session = Depends(get_db)):
    if crud.is_user_exist(db, user_in.username):
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = pwd_context.hash(user_in.password)
    user = models.User(
        id=str(uuid4()), username=user_in.username, password=hashed_password
    )
    crud.add_user(db, user)
    return schemas.UserOut(
        username=user_in.username,
        message="User created successfully",
        # id=user.id,
    )


# 用户登录
@app.post("/users/login", response_model=schemas.Token)
async def login_user_token(user_in: schemas.UserIn, db: Session = Depends(get_db)):
    if crud.is_not_valid_user(db, user_in):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token(data={"sub": user_in.username})
    return schemas.Token(access_token=access_token, token_type="bearer")


# 更新access_token
@app.post("/users/refresh", response_model=schemas.Token)
async def refresh_token(Authorization: Optional[str] = Header(None)):
    access_token = auth.get_access_token_from_Authorization(Authorization)
    username: str = get_current_username(access_token)

    ##
    ##  通过access_token获取用户名，然后再生成新的access_token
    access_token = create_access_token(data={"sub": username})

    test_username = get_current_username(access_token)

    if not test_username == username:
        raise HTTPException(status_code=401, detail="refresh token failed")
    return schemas.Token(access_token=access_token, token_type="bearer")


# 删除用户
@app.delete("/users/delete", response_model=schemas.UserOut)
async def delete_user(
    id: str, Authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
):
    access_token: str = auth.get_access_token_from_Authorization(Authorization)
    current_username: str = get_current_username(access_token)
    user = crud.get_user_by_id(db, id)
    if not (user.username == current_username):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    crud.delete_user_from_db(db, user)
    if os.path.exists(user.profile_image):
        os.remove(user.profile_image)
    logger.warning(f"User {current_username} deleted")
    return schemas.UserOut(
        # id=id,
        username=current_username,
        message="User deleted successfully.",
    )


# 获取用户ID
@app.post("/users/getid", response_model=schemas.UserOut)
async def get_user_id(
    user_in: schemas.UserIn,
    Authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):

    if crud.is_not_valid_user(db, user_in):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = auth.get_access_token_from_Authorization(Authorization)

    username: str = get_current_username(access_token)

    if username != user_in.username:

        raise HTTPException(status_code=401, detail="Invalid username or password")

    user = crud.get_user_by_username(db, username)

    return schemas.UserOut(id=user.id, username=user.username, message="User found.")


# 获取用户信息
@app.post("/users/me", response_model=schemas.UserShow)
async def read_users_me(
    user_in: schemas.UserIn,
    Authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    if crud.is_not_valid_user(db, user_in):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = auth.get_access_token_from_Authorization(Authorization)
    username: str = get_current_username(access_token)
    user = crud.get_user_by_username(db, username=username)
    return schemas.UserShow(
        message="info of current user",
        id=user.id,
        username=user.username,
        register_time=user.register_time,
        files=crud.get_file_id_list(db, user),
    )


# 删除用户的所有文件
@app.delete("/users/files/delete", response_model=schemas.UserOut)
async def delete_user_files(
    Authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
):

    access_token = auth.get_access_token_from_Authorization(Authorization)
    username: str = get_current_username(access_token)
    user = crud.get_user_by_username(db, username=username)
    for file in user.files:
        crud.delete_file_from_db(db, file)
    if not crud.is_user_files_empty(db, user):
        raise HTTPException(status_code=500, detail="Delete files failed")
    return schemas.UserOut(
        # id=user.id,
        username=user.username,
        message="All files deleted successfully.",
    )


#  上传文件
@app.post("/files/upload", response_model=schemas.FileOut)
async def upload_file(
    file: UploadFile = File(...),
    file_id: Optional[str] = None,
    file_nodes: Optional[str] = None,
    Authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):

    access_token = auth.get_access_token_from_Authorization(Authorization)

    username: str = get_current_username(access_token)

    user = crud.get_user_by_username(db, username)

    # 可选参数file_id，如果指定了file_id，检查文件是否已存在，防止重复上传，前端先计算文件内容的哈希值作为文件ID
    if file_id:
        try:
            # 这里没有是会抛出异常，所以不需要判断是否存在
            crud.get_file_by_id(db, file_id=file_id)
        except:
            pass
        else:
            # 如果文件已存在，抛出异常
            filem = crud.get_file_by_id(db, file_id=file_id)
            # file
            if os.path.exists(filem.file_path):
                logger.warning(f"File {filem.filename} already exists")
                raise HTTPException(status_code=400, detail="File already exists")

    if file_nodes:

        file_nodes = json.loads(file_nodes)

        if len(numpy.array(file_nodes).shape) != 1:
            logger.error("invalid upload nodes")
            raise HTTPException(status_code=400, detail="invalid nodes")
        for node in file_nodes:
            if not node.strip():
                logger.warning(
                    "The head of File nodes is empty, please input a valid node name. default: []"
                )
                file_nodes = []
                break
    else:
        file_nodes = []

    # 计算文件内容的哈希值作为文件ID
    file_content = await file.read()
    # 文件内容的哈希值 + 用户名哈希值 + 节点哈希值 作为文件ID
    file_hash = (
        hashlib.sha256(file_content).hexdigest()
        + hashlib.sha1(username.encode()).hexdigest()
        + hashlib.sha1("".join(file_nodes).encode()).hexdigest()
    )

    # 检查文件是否已存在
    existing_file = (
        db.query(models.File)
        .filter(models.File.id == file_hash, models.File.file_owner_name == username)
        .first()
    )

    if existing_file:
        return schemas.FileOut(
            id=existing_file.id,
            filename=existing_file.filename,
            file_size=existing_file.file_size,
            message="File already exists",
            file_create_time=existing_file.file_create_time,
            file_type=existing_file.file_type,
            file_owner_name=existing_file.file_owner_name,
            file_nodes=existing_file.file_nodes,
            file_download_link=f"/file/download/{user.id}/{existing_file.id}/{existing_file.filename}",
        )

    filename = file.filename

    filename = os.path.basename(filename)  # 获取基本路径

    file_type = filename.split(".")[-1] if "." in filename else "binary"

    file_path = utility.get_new_path(
        os.path.join(config.Config.UPLOAD_PATH, username, file_type, filename)
    )

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    async with aiofiles.open(file_path, "wb") as buffer:
        await buffer.write(file_content)

    file_size = str(os.path.getsize(file_path))
    file_create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logger.debug(f"Upload file_nodes: {file_nodes}")

    new_file = models.File(
        id=file_hash,
        filename=filename,
        file_path=file_path,
        file_size=file_size,
        file_owner_name=username,
        file_create_time=file_create_time,
        file_type=file_type,
        file_nodes=file_nodes,
    )

    # 添加文件到用户的文件列表
    crud.add_file_to_user(db, new_file, user)

    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    if not new_file == crud.get_file_by_id(db, file_id=new_file.id):
        raise HTTPException(status_code=500, detail="Upload file failed")

    return schemas.FileOut(
        id=new_file.id,
        filename=new_file.filename,
        file_size=new_file.file_size,
        message="Upload file successful",
        file_create_time=new_file.file_create_time,
        file_type=new_file.file_type,
        file_owner_name=new_file.file_owner_name,
        file_nodes=new_file.file_nodes,
        file_download_link=f"/file/download/{user.id}/{new_file.id}/{new_file.filename}",
    )


@app.get("/files/download")
async def read_file(
    file_id: str,
    Authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):

    access_token = auth.get_access_token_from_Authorization(Authorization)

    username: str = get_current_username(access_token)

    user = crud.get_user_by_username(db, username)

    file = crud.get_file_by_id(db, file_id=file_id)

    if file.file_owner_name != user.username:

        raise HTTPException(status_code=403, detail="Permission denied")

    if not crud.is_fileid_in_user_files(db, user, file.id):

        raise HTTPException(
            status_code=404, detail="File not found in user's file list"
        )

    if not os.path.exists(file.file_path):

        raise HTTPException(status_code=404, detail="File path not found")

    logger.debug(f"Download file: {file.file_path}")

    return FileResponse(
        file.file_path,
        media_type="application/octet-stream",
        filename=os.path.basename(file.file_path),
    )


async def file_iterator(file_path: str, start: int, end: int):
    async with aiofiles.open(file_path, mode="rb") as f:
        await f.seek(start)
        chunk_size = 1024
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


@app.get("/files/download/stream")
async def read_file_stream(
    request: Request,
    file_id: str,
    Authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    access_token = auth.get_access_token_from_Authorization(Authorization)
    username: str = get_current_username(access_token)
    user = crud.get_user_by_username(db, username)
    file = crud.get_file_by_id(db, file_id=file_id)

    if file.file_owner_name != user.username:
        raise HTTPException(status_code=403, detail="Permission denied")

    if not crud.is_fileid_in_user_files(db, user, file.id):
        raise HTTPException(
            status_code=404, detail="File not found in user's file list"
        )

    if not os.path.exists(file.file_path):
        raise HTTPException(status_code=404, detail="File path not found")

    file_size = os.path.getsize(file.file_path)
    range_header = request.headers.get("Range")
    if range_header:
        start, end = range_header.replace("bytes=", "").split("-")
        start = int(start)
        end = int(end) if end else file_size - 1
    else:
        start = 0
        end = file_size - 1

    if start >= file_size or end >= file_size:
        raise HTTPException(status_code=416, detail="Requested Range Not Satisfiable")

    return StreamingResponse(
        file_iterator(file.file_path, start, end),
        status_code=206 if range_header else 200,
        headers={
            "Content-Length": str(end - start + 1),
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
        },
    )


# 获取用户文件列表
@app.get("/files/list", response_model=schemas.FileList)
async def list_files(
    Authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
):

    access_token = auth.get_access_token_from_Authorization(Authorization)

    username: str = get_current_username(access_token)

    user = crud.get_user_by_username(db, username)

    file_list = list(
        schemas.FileOut(
            id=file.id,
            filename=file.filename,
            file_size=file.file_size,
            message="File found",
            file_create_time=file.file_create_time,
            file_type=file.file_type,
            file_owner_name=file.file_owner_name,
            file_nodes=file.file_nodes,
            file_download_link=f"/file/download/{user.id}/{file.id}/{file.filename}",
        )
        for file in user.files
    )

    return dict(files=file_list)


# 删除一个文件
@app.delete("/files/delete", response_model=schemas.FileOut)
async def delete_file(
    file_id: str,
    Authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):

    access_token = auth.get_access_token_from_Authorization(Authorization)

    username: str = get_current_username(access_token)

    user: models.User = crud.get_user_by_username(db, username)

    file: models.File = crud.get_file_by_id(db, file_id=file_id)

    if file.file_owner_name != user.username:

        raise HTTPException(status_code=403, detail="Permission denied")

    if not crud.is_file_in_user_files(db, user, file):

        raise HTTPException(
            status_code=404, detail="File not found in user's file list"
        )

    if not os.path.exists(file.file_path):

        raise HTTPException(status_code=404, detail="File path not found")

    crud.delete_file_from_db(db, file)

    return schemas.FileOut(
        message="File deleted successfully",
        id=file.id,
        filename=file.filename,
        file_size=file.file_size,
        file_create_time=file.file_create_time,
        file_type=file.file_type,
        file_owner_name=file.file_owner_name,
        file_nodes=file.file_nodes,
    )


@app.post("/db/reset", response_model=schemas.DbOut)
async def reset_db(user_in: schemas.UserIn, db: Session = Depends(get_db)):
    if (
        user_in.username != config.Config.ROOT_USER
        or user_in.password != config.Config.ROOT_PASSWORD
    ):
        raise HTTPException(status_code=403, detail="Permission denied")
    db.query(models.association_table).delete()  # 清空联系表
    db.query(models.User).delete()  # 清空用户表
    db.query(models.File).delete()  # 清空文件表
    db.commit()
    if os.path.exists(config.onfig.UPLOAD_PATH):
        shutil.rmtree(config.Config.UPLOAD_PATH)
    return schemas.DbOut(
        message="Database reset successfully and all files deleted.",
        user_count=db.query(models.User).count(),
        file_count=db.query(models.File).count(),
    )


# 获取单个文件信息
@app.get("/files/info", response_model=schemas.FileOut)
async def file_info(
    file_id: str,
    Authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):

    access_token = auth.get_access_token_from_Authorization(Authorization)

    username: str = get_current_username(access_token)

    user = crud.get_user_by_username(db, username)

    file = crud.get_file_by_id(db, file_id=file_id)

    if file.file_owner_name != user.username:

        raise HTTPException(status_code=403, detail="Permission denied")

    if not crud.is_file_in_user_files(db, user, file):

        raise HTTPException(
            status_code=404, detail="File not found in user's file list"
        )

    if not os.path.exists(file.file_path):

        raise HTTPException(status_code=404, detail="File path not found")

    return schemas.FileOut(
        id=file.id,
        filename=file.filename,
        file_size=file.file_size,
        message="File found",
        file_create_time=file.file_create_time,
        file_type=file.file_type,
        file_owner_name=file.file_owner_name,
        file_path=file.file_path,
        file_nodes=file.file_nodes,
    )


# 移动文件位置
@app.post("/file/modifynodes", response_model=schemas.FileOut)
async def modify_file_nodes(
    file_id: str,
    file_nodes: Optional[str] = None,
    Authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    if not file_nodes:
        raise HTTPException(status_code=405, detail="Invalid nodes")
    else:
        # logger.debug(f"{file_nodes}")

        file_nodes_array = json.loads(file_nodes)

    if len(numpy.array(file_nodes_array).shape) != 1:
        logger.error("invalid upload nodes")
        raise HTTPException(status_code=400, detail="invalid nodes")
    for node in file_nodes_array:
        if not node.strip():
            logger.warning(
                "The head of File nodes is empty, please input a valid node name. default: []"
            )
            file_nodes_array = []
            break

    access_token = auth.get_access_token_from_Authorization(Authorization)

    username = get_current_username(access_token)

    file = crud.get_file_by_id(db, file_id)

    if file.file_owner_name != username:
        # print()
        logger.debug({logger.debug(file.file_owner_name)} / {username})
        raise HTTPException(status_code=401, detail="Access denied")
    else:
        # if file.file_nodes == file_nodes_array:
        file.file_nodes = file_nodes_array

    db.commit()

    if file.file_nodes != file_nodes_array:

        raise HTTPException(status_code=403, detail="Modify nodes failes")

    else:

        logger.debug(f"upload: {file_nodes} , new nodes {file.file_nodes}")

    return schemas.FileOut(
        id=file.id,
        filename=file.filename,
        file_size=file.file_size,
        message="modify file_nodes successful",
        file_create_time=file.file_create_time,
        file_type=file.file_type,
        file_owner_name=file.file_owner_name,
        # file_path=file.file_path,
        file_nodes=file.file_nodes,
    )


# @app.get("/file/download/{user_id}/{file_id}/{file_name}")
# async def download_file(
#     user_id: str, file_id: str, file_name: str, db: Session = Depends(get_db)
# ):
#     user = crud.get_user_by_id(db, user_id)
#     file = crud.get_file_by_id(db, file_id)
#     if not file:
#         raise HTTPException(status_code=404, detail="File not found")
#     if file.file_owner_name != user.username or file.filename != file_name:
#         raise HTTPException(status_code=403, detail="Permission denied")

#     file_path = Path(file.file_path)
#     file_size = file_path.stat().st_size

#     return FileResponse(
#         file.file_path,
#         filename=file.filename,
#         media_type="application/octet-stream",
#         headers={"Content-Length": str(file_size)},
#     )


@app.get("/file/download/{user_id}/{file_id}/{file_name}")
async def download_file(
    request: Request,
    user_id: str,
    file_id: str,
    file_name: str,
    db: Session = Depends(get_db),
):
    user = crud.get_user_by_id(db, user_id)
    file = crud.get_file_by_id(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    if file.file_owner_name != user.username or file.filename != file_name:
        raise HTTPException(status_code=403, detail="Permission denied")

    if not os.path.exists(file.file_path):
        raise HTTPException(status_code=404, detail="File path not found")

    file_size = os.path.getsize(file.file_path)
    range_header = request.headers.get("Range")
    if range_header:
        start, end = range_header.replace("bytes=", "").split("-")
        start = int(start)
        end = int(end) if end else file_size - 1
    else:
        start = 0
        end = file_size - 1

    if start >= file_size or end >= file_size:
        raise HTTPException(status_code=416, detail="Requested Range Not Satisfiable")

    return StreamingResponse(
        file_iterator(file.file_path, start, end),
        status_code=206 if range_header else 200,
        headers={
            "Content-Length": str(end - start + 1),
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
        },
    )


# 修改文件名
@app.post("/file/modifyname", response_model=schemas.FileOut)
async def modify_file_name(
    file_id: str,
    new_file_name: str,
    Authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    if not new_file_name:
        raise HTTPException(status_code=405, detail="Invalid file name")
    access_token = auth.get_access_token_from_Authorization(Authorization)
    username = get_current_username(access_token)
    logger.debug(f"new file name: {new_file_name}")
    logger.debug(f"file_id: {file_id}")
    file = crud.get_file_by_id(db, file_id)
    if file.file_owner_name != username:
        raise HTTPException(status_code=401, detail="Access denied")
    else:
        file.filename = new_file_name
    db.commit()

    if file.filename != new_file_name:

        raise HTTPException(
            status_code=403, detail="Modify file name failes, Server error"
        )

    return schemas.FileOut(
        id=file.id,
        filename=file.filename,
        file_size=file.file_size,
        message="modify file name successful",
        file_create_time=file.file_create_time,
        file_type=file.file_type,
        file_owner_name=file.file_owner_name,
        file_nodes=file.file_nodes,
    )


# 获取同属于一个节点的文件列表
@app.get("/files/nodefiles", response_model=schemas.FileList)
async def list_node_files(
    file_nodes: str,  # 数组字符串
    Authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    if not file_nodes or len(numpy.array(json.loads(file_nodes)).shape) != 1:
        logger.error("invalid upload nodes, please input a string array, default: []")
        raise HTTPException(
            status_code=400,
            detail="invalid upload nodes, please input a string array, default: []",
        )

    access_token = auth.get_access_token_from_Authorization(Authorization)

    username: str = get_current_username(access_token)

    user = crud.get_user_by_username(db, username)

    file_list = list(
        schemas.FileOut(
            id=file.id,
            filename=file.filename,
            file_size=file.file_size,
            message="File found",
            file_create_time=file.file_create_time,
            file_type=file.file_type,
            file_owner_name=file.file_owner_name,
            file_nodes=file.file_nodes,
            file_download_link=f"/file/download/{user.id}/{file.id}/{file.filename}",
        )
        for file in user.files
        if file.file_nodes == json.loads(file_nodes)
    )

    return dict(files=file_list)


# 获取用户头像
@app.get("/users/profileimage", response_model=schemas.UserOut)
async def get_profile_image(
    Authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
):
    access_token = auth.get_access_token_from_Authorization(Authorization)
    username: str = get_current_username(access_token)
    user = crud.get_user_by_username(db, username)
    if not user.profile_image or not os.path.exists(user.profile_image):
        if os.path.exists(config.User.DEFAULT_PROFILE_IMAGE):
            user.profile_image = config.User.DEFAULT_PROFILE_IMAGE
        else:
            raise HTTPException(
                status_code=404,
                detail="Profile image not found, Server error, no default profile image",
            )
    return schemas.UserOut(
        id=user.id,
        username=user.username,
        profile_image=user.profile_image,
        message="Profile image found",
    )


# 上传用户头像
@app.post("/users/upload/profileimage", response_model=schemas.UserOut)
async def upload_profile_image(
    file: UploadFile = File(...),
    Authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    access_token = auth.get_access_token_from_Authorization(Authorization)
    username: str = get_current_username(access_token)
    user = crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    file_path = utility.get_new_path(
        os.path.join(config.Config.STATIC_PATH, username, "profile", file.filename)
    )
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    try:
        async with aiofiles.open(file_path, "wb") as buffer:
            await buffer.write(await file.read())
    except:
        raise HTTPException(
            status_code=500, detail="Profile image save failed, Server error"
        )
    user.profile_image = file_path

    db.commit()

    if not user.profile_image or not os.path.exists(user.profile_image):

        raise HTTPException(
            status_code=500, detail="Profile image upload failed, Server error"
        )

    return schemas.UserOut(
        id=user.id,
        username=user.username,
        profile_image=user.profile_image,
        message="Profile image uploaded successfully",
    )
