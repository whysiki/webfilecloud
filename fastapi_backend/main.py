# encoding: utf-8
from fastapi import HTTPException, Depends
from uuid import uuid4
from starlette.requests import Request
from sqlalchemy.orm import Session
from fastapi import File, UploadFile
from datetime import datetime, timedelta
from minio import Minio
from minio.error import S3Error
import hashlib
from fastapi.responses import StreamingResponse, Response
from loguru import logger
import json
import numpy
from concurrent.futures import ThreadPoolExecutor
import io
import asyncio
from urllib.parse import quote
import mimetypes
from auth import pwd_context, create_access_token, get_current_username  # auth
import config  # custom configuration
from config.status import StatusConfig as Status  # custom status codes
from dep import get_db, get_access_token  # inject dependency
from app import app  # fast app instance
import utility  # custom utility functions
import models  # model definition
import schemas  # pydantic schemas
import crud  # database operations
from storage_ import (
    handler as storage_,
)  # separate storage functions 别问我为什么这么导入🥲
from typing import List, Any, Optional, Tuple


# register user
@app.post("/users/register", response_model=schemas.UserOut)
async def register_user(user_in: schemas.UserIn, db: Session = Depends(get_db)):
    """
    Success: 200 OK

    Raises:

        HTTP_400_BAD_REQUEST (status code 400): If the user already exists.

        HTTP_500_INTERNAL_SERVER_ERROR (status code 500): If the user creation failed.

    """
    if crud.is_user_exist(db, user_in.username):
        raise HTTPException(
            status_code=Status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )
    hashed_password = pwd_context.hash(user_in.password)
    user = models.User(
        id=str(uuid4()), username=user_in.username, password=hashed_password
    )
    crud.add_user(db, user)
    return schemas.UserOut(
        id="",
        username=user_in.username,
        message="User created successfully",
        profile_image="",
        profile="",
        role="",
    )


# login user and return access_token and refresh_token
@app.post("/users/login", response_model=schemas.Token)
async def login_user_token(user_in: schemas.UserIn, db: Session = Depends(get_db)):
    """
    Raises:
        HTTP_401_UNAUTHORIZED (status code 401): If the user login failed.

        HTTP_404_NOT_FOUND: If the user is not found, raises HTTP 404 Not Found

        HTTP_500_INTERNAL_SERVER_ERROR if any other error occurs.
    """
    if crud.is_not_valid_user(db, user_in):
        raise HTTPException(
            status_code=Status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    access_token = create_access_token(data={"sub": user_in.username})
    __refresh_token = create_access_token(
        data={"sub": user_in.username},
        expires_delta=timedelta(minutes=config.Config.ACCESS_TOKEN_EXPIRE_MINUTES * 2),
    )
    return schemas.Token(
        access_token=access_token, token_type="bearer", refresh_token=__refresh_token
    )


# update access_token with refresh_token
@app.post("/users/refresh", response_model=schemas.Token)
async def refresh_token(access_token: str = Depends(get_access_token)):
    """
    Raises:
        HTTP_401_UNAUTHORIZED
    """
    username: str = get_current_username(access_token)
    # by leveraging the refresh token, the user can get a new access token
    access_token = create_access_token(data={"sub": username})
    __refresh_token = create_access_token(
        data={"sub": username},
        expires_delta=timedelta(minutes=config.Config.ACCESS_TOKEN_EXPIRE_MINUTES * 2),
    )
    test_username = get_current_username(access_token)
    test_username_refresh = get_current_username(__refresh_token)
    if not (test_username == username == test_username_refresh):
        raise HTTPException(
            status_code=Status.HTTP_401_UNAUTHORIZED, detail="refresh token failed"
        )
    logger.debug(f"refresh token :{__refresh_token}")
    return schemas.Token(
        access_token=access_token, token_type="bearer", refresh_token=__refresh_token
    )


# delete user
@app.delete("/users/delete", response_model=schemas.UserOut)
async def delete_user(
    id: str,
    access_token: str = Depends(get_access_token),
    db: Session = Depends(get_db),
):
    current_username: str = get_current_username(access_token)
    user = crud.get_user_by_id(db, id)
    if not (str(user.username) == str(current_username)):
        raise HTTPException(
            status_code=Status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    crud.delete_user_from_db(db, user)
    if str(user.profile_image):
        storage_.remove_file(user.profile_image)
    logger.warning(f"User {current_username} deleted")
    return schemas.UserOut(
        # id=id,
        username=current_username,
        message="User deleted successfully.",
    )


# get user id
@app.post("/users/getid", response_model=schemas.UserOut)
async def get_user_id(
    user_in: schemas.UserIn,
    access_token: str = Depends(get_access_token),
    db: Session = Depends(get_db),
):
    if crud.is_not_valid_user(db, user_in):
        raise HTTPException(
            status_code=Status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    username: str = get_current_username(access_token)

    if username != user_in.username:
        raise HTTPException(
            status_code=Status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    user = crud.get_user_by_username(db, username)

    return schemas.UserOut(id=user.id, username=user.username, message="User found.")


# get user info
@app.post("/users/me", response_model=schemas.UserShow)
async def read_users_me(
    user_in: schemas.UserIn,
    access_token: str = Depends(get_access_token),
    db: Session = Depends(get_db),
):
    """
    HTTP_401_UNAUTHORIZED

    HTTP_404_NOT_FOUND: If the user is not found, raises HTTP 404 Not Found

    HTTP_500_INTERNAL_SERVER_ERROR if any other error occurs.
    """
    if crud.is_not_valid_user(db, user_in):
        raise HTTPException(
            status_code=Status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    username: str = get_current_username(access_token)
    user = crud.get_user_by_username(db, username=username)
    return schemas.UserShow(
        message="info of current user",
        id=user.id,
        username=user.username,
        register_time=user.register_time,
        files=crud.get_file_id_list(db, user),
    )


# delete all users , dangerous api, not recommended for production
@app.delete("/users/files/delete", response_model=schemas.UserOut)
@utility.require_double_confirmation
async def delete_user_files(
    access_token: str = Depends(get_access_token), db: Session = Depends(get_db)
):
    username: str = get_current_username(access_token)
    user = crud.get_user_by_username(db, username=username)
    for file in user.files:
        crud.delete_file_from_db(db, file)
    if not crud.is_user_files_empty(db, user):
        raise HTTPException(
            status_code=Status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Delete files failed",
        )
    return schemas.UserOut(
        # id=user.id,
        username=user.username,
        message="All files deleted successfully.",
    )


# upload file, suitable for files that are not too large
@app.post("/files/upload", response_model=schemas.FileOut)
async def upload_file(
    file: UploadFile = File(...),
    file_id: Optional[str] = None,
    file_nodes: Optional[str] = None,
    access_token: str = Depends(get_access_token),
    db: Session = Depends(get_db),
):
    username: str = get_current_username(access_token)

    user = crud.get_user_by_username(db, username)

    if file_id:  # if file_id is not None, check if the file already exists
        try:
            # if file_id is not exist, raise an exception
            crud.get_file_by_id(db, file_id=file_id)
        except:
            # if file_id is not exist, do nothing
            logger.debug(f"file_id: {file_id} not exist, upload new file")
            # pass
        else:
            # otherwise, raise an exception
            filem = crud.get_file_by_id(db, file_id=file_id)
            if storage_.is_file_exist(filem.file_path):
                raise HTTPException(
                    status_code=Status.HTTP_400_BAD_REQUEST,
                    detail="File already exists",
                )

    file_nodes_list: List[str]

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

    file_content: bytes = await file.read()
    # the file content hash + the user name hash + the file node hash 🤣
    file_content_hash = hashlib.sha256(file_content).hexdigest()
    file_hash = (
        file_content_hash
        + hashlib.sha1(username.encode()).hexdigest()
        + hashlib.sha1("".join(file_nodes_list).encode()).hexdigest()
    )

    # check if the file already exists
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

    # new file

    filename = storage_.get_path_basename(file.filename)

    file_type = filename.split(".")[-1] if "." in filename else "binary"

    prepare_file_path = storage_.get_join_path(
        config.Config.UPLOAD_PATH, f"{file_content_hash}.{file_type}"
    )

    file_path = prepare_file_path

    # storage_.makedirs(file_path)

    await storage_.async_write_file_wb(file_path, file_content)

    file_size = str(storage_.get_file_size(file_path))
    file_create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logger.debug(f"Upload file_nodes: {file_nodes_list}")

    new_file = models.File(
        id=file_hash,
        filename=filename,
        file_path=file_path,
        file_size=file_size,
        file_owner_name=username,
        file_create_time=file_create_time,
        file_type=file_type,
        file_nodes=file_nodes_list,
    )

    crud.add_file_to_user(db, new_file, user)

    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    if not new_file == crud.get_file_by_id(db, file_id=new_file.id):
        raise HTTPException(
            status_code=Status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Upload file failed",
        )

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


# download file with direct filereponse
@app.get("/files/download")
async def read_file(
    file_id: str,
    access_token: str = Depends(get_access_token),
    db: Session = Depends(get_db),
):
    username: str = get_current_username(access_token)

    user = crud.get_user_by_username(db, username)

    file = crud.get_file_by_id(db, file_id=file_id)

    if file.file_owner_name != user.username:
        raise HTTPException(
            status_code=Status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    if not crud.is_fileid_in_user_files(db, user, file.id):
        raise HTTPException(
            status_code=Status.HTTP_404_NOT_FOUND,
            detail="File not found in user's file list",
        )

    if not storage_.is_file_exist(file.file_path):
        raise HTTPException(
            status_code=Status.HTTP_404_NOT_FOUND, detail="File path not found"
        )

    logger.debug(f"Download file: {file.file_path}")

    return StreamingResponse(
        io.BytesIO(storage_.get_file_bytestream(file.file_path)),  # type: ignore
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={quote(file.filename)}"},
    )


# download file with stream response
@app.get("/files/download/stream")
async def read_file_stream(
    request: Request,
    file_id: str,
    access_token: str = Depends(get_access_token),
    db: Session = Depends(get_db),
):
    username: str = get_current_username(access_token)
    user = crud.get_user_by_username(db, username)
    file = crud.get_file_by_id(db, file_id=file_id)

    if file.file_owner_name != user.username:
        raise HTTPException(
            status_code=Status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    if not crud.is_fileid_in_user_files(db, user, file.id):
        raise HTTPException(
            status_code=Status.HTTP_404_NOT_FOUND,
            detail="File not found in user's file list",
        )

    if not storage_.is_file_exist(file.file_path):
        raise HTTPException(
            status_code=Status.HTTP_404_NOT_FOUND, detail="File path not found"
        )

    file_size = storage_.get_file_size(file.file_path)
    range_header = request.headers.get("Range", "")
    start, end = utility.get_start_end_from_range_header(range_header, file_size)

    return StreamingResponse(
        storage_.file_iterator(file.file_path, start, end),
        status_code=(
            Status.HTTP_206_PARTIAL_CONTENT if range_header else Status.HTTP_200_OK
        ),
        headers={
            "Content-Length": str(end - start + 1),
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
        },
    )


# get file list of current user
@app.get("/files/list", response_model=schemas.FileList)
async def list_files(
    access_token: str = Depends(get_access_token), db: Session = Depends(get_db)
):
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


# delete file of current user
@app.delete("/files/delete", response_model=schemas.FileOut)
async def delete_file(
    file_id: str,
    access_token: str = Depends(get_access_token),
    db: Session = Depends(get_db),
):
    username: str = get_current_username(access_token)

    user: models.User = crud.get_user_by_username(db, username)

    file: models.File = crud.get_file_by_id(db, file_id=file_id)

    if str(file.file_owner_name) != str(user.username):
        raise HTTPException(
            status_code=Status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    if not crud.is_file_in_user_files(db, user, file):
        raise HTTPException(
            status_code=Status.HTTP_404_NOT_FOUND,
            detail="File not found in user's file list",
        )

    if not storage_.is_file_exist(file.file_path):  # type: ignore

        raise HTTPException(
            status_code=Status.HTTP_404_NOT_FOUND, detail="File path not found"
        )

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


# reset database, dangerous api, not recommended for production
@app.post("/db/reset", response_model=schemas.DbOut)
async def reset_db(user_in: schemas.UserIn, db: Session = Depends(get_db)):
    if (
        user_in.username != config.Config.ROOT_USER
        or user_in.password != config.Config.ROOT_PASSWORD
    ):
        raise HTTPException(
            status_code=Status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )
    db.query(models.association_table).delete()
    db.query(models.User).delete()
    db.query(models.File).delete()
    db.commit()
    storage_.remove_path(config.Config.UPLOAD_PATH)
    storage_.remove_path(config.Config.STATIC_PATH)
    storage_.remove_path(config.FileConfig.M3U8_INDEX_PATH)
    storage_.remove_path(config.FileConfig.PREVIEW_FILES_PATH)
    if hasattr(config.StorageConfig, "TEMP_UPLOAD_DIR"):
        storage_.remove_path(config.StorageConfig.TEMP_UPLOAD_DIR)
    # if storage_.is_file_exist(config.UserConfig.DEFAULT_PROFILE_IMAGE):
    # storage_.remove_file(config.UserConfig.DEFAULT_PROFILE_IMAGE)
    # if storage_.is_file_exist(config.FileConfig.LOAD_ERROR_IMG):
    # storage_.remove_file(config.FileConfig.LOAD_ERROR_IMG)
    return schemas.DbOut(
        message="Database reset successfully and all files deleted.",
        user_count=db.query(models.User).count(),
        file_count=db.query(models.File).count(),
    )


# modify file name
@app.post("/file/modifyname", response_model=schemas.FileOut)
async def modify_file_name(
    file_id: str,
    new_file_name: str,
    access_token: str = Depends(get_access_token),
    db: Session = Depends(get_db),
):
    if not new_file_name:
        raise HTTPException(
            status_code=Status.HTTP_400_BAD_REQUEST, detail="Invalid file name"
        )

    username = get_current_username(access_token)
    logger.debug(f"new file name: {new_file_name}")
    logger.debug(f"file_id: {file_id}")
    file = crud.get_file_by_id(db, file_id)
    if file.file_owner_name != username:
        raise HTTPException(
            status_code=Status.HTTP_401_UNAUTHORIZED, detail="Access denied"
        )
    else:
        file.filename = new_file_name
    db.commit()

    if file.filename != new_file_name:
        raise HTTPException(
            status_code=Status.HTTP_403_FORBIDDEN,
            detail="Modify file name failes, Server error",
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


# get single file info
@app.get("/files/info", response_model=schemas.FileOut)
async def file_info(
    file_id: str,
    access_token: str = Depends(get_access_token),
    db: Session = Depends(get_db),
):
    username: str = get_current_username(access_token)

    user = crud.get_user_by_username(db, username)

    file = crud.get_file_by_id(db, file_id=file_id)

    if file.file_owner_name != user.username:
        raise HTTPException(
            status_code=Status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    if not crud.is_file_in_user_files(db, user, file):
        raise HTTPException(
            status_code=Status.HTTP_404_NOT_FOUND,
            detail="File not found in user's file list",
        )

    # if not storage_.is_file_exist(file.file_path):
    if not storage_.is_file_exist(file.file_path):
        raise HTTPException(
            status_code=Status.HTTP_404_NOT_FOUND, detail="File path not found"
        )

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


# modify file nodes
@app.post("/file/modifynodes", response_model=schemas.FileOut)
async def modify_file_nodes(
    file_id: str,
    file_nodes: Optional[str] = None,
    access_token: str = Depends(get_access_token),
    db: Session = Depends(get_db),
):
    if not file_nodes:
        raise HTTPException(
            status_code=Status.HTTP_400_BAD_REQUEST, detail="Invalid nodes"
        )
    else:

        file_nodes_array: List[str] = json.loads(file_nodes)

    if len(numpy.array(file_nodes_array).shape) != 1:
        logger.error("invalid upload nodes")
        raise HTTPException(
            status_code=Status.HTTP_400_BAD_REQUEST, detail="invalid nodes"
        )
    for node in file_nodes_array:
        if not node.strip():
            logger.warning(
                "The head of File nodes is empty, please input a valid node name. default: []"
            )
            file_nodes_array = []
            break

    username = get_current_username(access_token)

    file = crud.get_file_by_id(db, file_id)

    if file.file_owner_name != username:
        # print()
        logger.error(
            f"Not the owner of the file: {file.file_owner_name}. file : {file.filename}"
        )
        raise HTTPException(
            status_code=Status.HTTP_401_UNAUTHORIZED, detail="Access denied"
        )
    else:
        # if file.file_nodes == file_nodes_array:
        file.file_nodes = file_nodes_array

    db.commit()

    if tuple(file.file_nodes) != tuple(file_nodes_array):

        raise HTTPException(
            status_code=Status.HTTP_403_FORBIDDEN, detail="Modify nodes failes"
        )

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


# direct download file, direct link, actually may need to generate a temporary link, to be optimized
@app.get("/file/directdownload/{user_id}/{file_id}/{file_name}")
async def download_file_directdownload(
    user_id: str, file_id: str, file_name: str, db: Session = Depends(get_db)
):
    user = crud.get_user_by_id(db, user_id)
    file = crud.get_file_by_id(db, file_id)
    if not file:
        raise HTTPException(
            status_code=Status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    if file.file_owner_name != user.username or file.filename != file_name:
        raise HTTPException(
            status_code=Status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    if not storage_.is_file_exist(file.file_path):
        raise HTTPException(
            status_code=Status.HTTP_404_NOT_FOUND, detail="File path not found"
        )

    file_size = storage_.get_file_size(file.file_path)

    return StreamingResponse(
        io.BytesIO(storage_.get_file_bytestream(file.file_path)),  # type: ignore
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={quote(file.filename)}",
            "Content-Length": str(file_size) + "bytes",
        },
    )


# download file with stream response
@app.get("/file/download/{user_id}/{file_id}/{file_name}")
async def download_file_stream(
    request: Request,
    user_id: str,
    file_id: str,
    file_name: str,
    db: Session = Depends(get_db),
):
    user = crud.get_user_by_id(db, user_id)
    file = crud.get_file_by_id(db, file_id)
    if not file:
        raise HTTPException(
            status_code=Status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    if file.file_owner_name != user.username or file.filename != file_name:
        raise HTTPException(
            status_code=Status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    # if not storage_.is_file_exist(file.file_path):
    if not storage_.is_file_exist(file.file_path):
        raise HTTPException(
            status_code=Status.HTTP_404_NOT_FOUND, detail="File path not found"
        )

    # file_size = storage_.get_file_size(file.file_path)
    file_size = storage_.get_file_size(file.file_path)
    range_header = request.headers.get("Range", "")

    start, end = utility.get_start_end_from_range_header(range_header, file_size)

    return StreamingResponse(
        storage_.file_iterator(file.file_path, start, end),
        status_code=(
            Status.HTTP_206_PARTIAL_CONTENT if range_header else Status.HTTP_200_OK
        ),
        headers={
            "Content-Length": str(end - start + 1),
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
        },
    )


# get files of the same node
@app.get("/files/nodefiles", response_model=schemas.FileList)
async def list_node_files(
    file_nodes: str,  # array string , example: "['node1','node2']"
    access_token: str = Depends(get_access_token),
    db: Session = Depends(get_db),
):
    if not file_nodes or len(numpy.array(json.loads(file_nodes)).shape) != 1:
        logger.error("invalid upload nodes, please input a string array, default: []")
        raise HTTPException(
            status_code=Status.HTTP_400_BAD_REQUEST,
            detail="invalid upload nodes, please input a string array, default: []",
        )

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


# get user profile image
@app.get("/users/profileimage", response_model=schemas.UserOut)
async def get_profile_image(
    access_token: str = Depends(get_access_token), db: Session = Depends(get_db)
):
    username: str = get_current_username(access_token)
    user = crud.get_user_by_username(db, username)
    if not user.profile_image or not storage_.is_file_exist(user.profile_image):
        user.profile_image = (
            config.UserConfig.DEFAULT_PROFILE_IMAGE
        )  # this ia a system path
        storage_.save_file_from_system_path(
            user.profile_image, user.profile_image, delete_original=False
        )  # save the default profile image to the storage layer
        if storage_.is_file_exist(user.profile_image):
            logger.warning("default profile_image")
        else:
            logger.error(
                f"Profile image {user.profile_image} not found, Server error, no default profile image"
            )
            raise HTTPException(
                status_code=Status.HTTP_404_NOT_FOUND,
                detail="Profile image not found, Server error, no default profile image",
            )

    if not user.profile_image or not storage_.is_file_exist(user.profile_image):
        raise HTTPException(
            status_code=Status.HTTP_404_NOT_FOUND,
            detail="Profile image not found, Server error",
        )

    return StreamingResponse(
        io.BytesIO(storage_.get_file_bytestream(user.profile_image)),  # type: ignore
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={quote(storage_.get_path_basename(user.profile_image))}"
        },
    )


# upload user profile image
@app.post("/users/upload/profileimage", response_model=schemas.UserOut)
async def upload_profile_image(
    file: UploadFile = File(...),
    access_token: str = Depends(get_access_token),
    db: Session = Depends(get_db),
):
    username: str = get_current_username(access_token)
    user = crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=Status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # save profile image
    file_path = utility.get_new_path(
        storage_.get_join_path(
            config.Config.STATIC_PATH, username, "profile", file.filename
        )
    )
    # storage_.makedirs(file_path, isfile=True)

    total_size = 0

    file_content: bytearray = bytearray()

    while True:

        chunk = await file.read(1024)

        if not chunk:
            break

        total_size += len(chunk)

        if total_size > config.UserConfig.PROFILE_IMAGE_MAX_FILE_SIZE:

            if storage_.is_file_exist(file_path):
                storage_.remove_file(file_path)

            logger.warning("profile image File size exceeds maximum limit")

            raise HTTPException(
                status_code=Status.HTTP_400_BAD_REQUEST,
                detail="profile image File size exceeds maximum limit",
            )

        file_content.extend(chunk)

    await storage_.async_write_file_wb(file_path, bytes(file_content))

    user.profile_image = file_path

    db.commit()

    if not user.profile_image or not storage_.is_file_exist(user.profile_image):
        raise HTTPException(
            status_code=Status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile image upload failed, Server error",
        )

    return schemas.UserOut(
        username=user.username,
        profile_image=user.profile_image,
        message="Profile image uploaded successfully",
        id="",
    )


# prvivew image
@app.get("/files/img/preview")
async def preview_file(
    file_id: str,
    access_token: str = Depends(get_access_token),
    db: Session = Depends(get_db),
):
    username: str = get_current_username(access_token)
    user = crud.get_user_by_username(db, username)
    file = crud.get_file_by_id(db, file_id=file_id)

    if file.file_owner_name != user.username:
        raise HTTPException(
            status_code=Status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    if not crud.is_fileid_in_user_files(db, user, file.id):
        raise HTTPException(
            status_code=Status.HTTP_404_NOT_FOUND,
            detail="File not found in user's file list",
        )

    file.file_preview_path = storage_.get_join_path(
        config.FileConfig.PREVIEW_FILES_PATH, f"{file.id}_preview.{file.file_type}"
    )

    if (
        not file.file_preview_path
        or not storage_.is_file_exist(file.file_preview_path)
        or storage_.get_file_size(file.file_preview_path) <= 1.3 * 1024
    ):

        logger.debug(f"generate preview img :{file.filename}")

        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=4) as executor:
            thumbnail_data = await loop.run_in_executor(
                executor, utility.generate_thumbnail, file.file_path
            )

        await storage_.async_write_file_wb(file.file_preview_path, thumbnail_data)

    else:

        thumbnail_data = await storage_.async_read_file_rb(file.file_preview_path)

    db.commit()

    mime_type, _ = mimetypes.guess_type(file.file_path)

    filename = quote(storage_.get_path_basename(file.file_path))

    return StreamingResponse(
        io.BytesIO(thumbnail_data),
        media_type=mime_type,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )


# video preview
@app.get("/files/video/preview")
async def preview_video_file(
    file_id: str,
    access_token: str = Depends(get_access_token),
    db: Session = Depends(get_db),
):
    username: str = get_current_username(access_token)
    user = crud.get_user_by_username(db, username)
    file = crud.get_file_by_id(db, file_id=file_id)

    if file.file_owner_name != user.username:
        raise HTTPException(
            status_code=Status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    if not crud.is_fileid_in_user_files(db, user, file.id):
        raise HTTPException(
            status_code=Status.HTTP_404_NOT_FOUND,
            detail="File not found in user's file list",
        )

    if (
        not file.file_preview_path
        or not storage_.is_file_exist(file.file_preview_path)
        or storage_.get_file_size(file.file_preview_path) < 100
    ):
        logger.debug(f"generate preview video :{file.filename}")

        file.file_preview_path = storage_.get_join_path(
            config.FileConfig.PREVIEW_FILES_PATH, f"{file.id}_preview.mp4"
        )
        # storage_.makedirs(file.file_preview_path, is_file=True)
        utility.generate_preview_video(file.file_path, file.file_preview_path)

        db.commit()

    mime_type = "video/mp4"

    filename = quote(storage_.get_path_basename(file.file_path).replace(".", "_"))

    if (
        storage_.is_file_exist(file.file_preview_path)
        and storage_.get_file_size(file.file_preview_path) > 0
    ):

        return StreamingResponse(
            io.BytesIO(storage_.get_file_bytestream(file.file_preview_path)),  # type: ignore
            media_type=mime_type,
            headers={
                "Content-Disposition": f"attachment; filename=preview_{filename}.mp4"
            },
        )
    else:
        raise HTTPException(
            status_code=Status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error: Preview file not found or empty",
        )


# get hls m3u8 file
@app.get("/file/video/{file_id}/index.m3u8")
async def get_hls_m3u8_list(file_id: str, db: Session = Depends(get_db)):
    file = crud.get_file_by_id(db, file_id)

    segment_index_path = storage_.get_join_path(
        config.FileConfig.M3U8_INDEX_PATH, file.id
    )

    index_m3u8_name = "index.m3u8"

    index_m3u8_path = storage_.get_join_path(segment_index_path, index_m3u8_name)

    if (
        not storage_.is_file_exist(index_m3u8_path)
        or storage_.get_file_size(index_m3u8_path) < 200
    ):

        try:
            utility.generate_hls_playlist(
                file.file_path,
                output_dir=segment_index_path,
                playlist_name=index_m3u8_name,
                file_id=str(uuid4()),
            )

        except Exception as e:

            logger.warning(f"{type(e)}{str(e)}")

            raise HTTPException(
                status_code=Status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate HLS playlist and segments",
            )
    try:
        return StreamingResponse(
            io.BytesIO(storage_.get_file_bytestream(index_m3u8_path)),  # type: ignore
            media_type="application/vnd.apple.mpegurl",
        )
    except Exception as e:
        logger.warning(f"{type(e)}{str(e)}")
        raise HTTPException(
            status_code=Status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{type(e)}{str(e)} Failed to get HLS playlist",
        )


# get hls m3u8 segment file
@app.get("/file/segments/{file_id}/{segment_name}")
async def get_segment(request: Request, file_id: str, segment_name: str):
    segment_path = storage_.get_join_path(
        f"{storage_.get_join_path(config.FileConfig.M3U8_INDEX_PATH, file_id)}",
        segment_name,
    )
    if not storage_.is_file_exist(segment_path):
        raise HTTPException(
            status_code=Status.HTTP_404_NOT_FOUND, detail="Segment not found"
        )

    file_size = storage_.get_file_size(segment_path)

    range_header = request.headers.get("Range", "")

    start, end = utility.get_start_end_from_range_header(range_header, file_size)

    return StreamingResponse(
        storage_.file_iterator(segment_path, start, end),
        status_code=(
            Status.HTTP_206_PARTIAL_CONTENT if range_header else Status.HTTP_200_OK
        ),
        headers={
            "Content-Length": str(end - start + 1),
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
        },
    )


# minio file storage specific code
if config.StorageConfig.STORE_TYPE == "minio":

    # 临时文件夹
    TEMP_UPLOAD_DIR = config.StorageConfig.TEMP_UPLOAD_DIR

    def get_minio_client():

        return config.StorageConfig.MinioClient

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
            print(f"Error getting size for {object_name}: {err}")
            return 0

    @app.get("/file/download/{bucket_name}/{object_name}")
    @app.head("/file/download/{bucket_name}/{object_name}")
    async def minio_download_file(
        request: Request,
        object_name: str,
        bucket_name: str,
        client: Minio = Depends(get_minio_client),
    ):
        file_size = minio_get_file_size(
            client=client, bucket_name=bucket_name, object_name=object_name
        )

        if not file_size:
            raise HTTPException(
                status_code=Status.HTTP_404_NOT_FOUND, detail="No file data."
            )

        if request.method == "HEAD":
            headers = {
                "Content-Length": str(file_size),
                "Accept-Ranges": "bytes",
            }
            return Response(headers=headers)

        range_header = request.headers.get("Range", "")

        start, end = utility.get_start_end_from_range_header(range_header, file_size)

        return StreamingResponse(
            minio_file_iterator(
                client=client,
                bucket_name=bucket_name,
                object_name=object_name,
                start=start,
                end=end,
            ),
            status_code=(
                Status.HTTP_206_PARTIAL_CONTENT if range_header else Status.HTTP_200_OK
            ),
            headers={
                "Content-Length": str(end - start + 1),
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
            },
        )

    # file_id is not object_name
    @app.post("/upload/")
    async def minio_upload_file(
        file_id: str, order: str, upload_file: UploadFile = File(...)
    ):
        try:
            logger.info(file_id, order)
            # 创建临时文件目录
            temp_upload_dir = storage_.get_join_path(TEMP_UPLOAD_DIR, file_id)
            # storage_.makedirs(temp_upload_dir, exist_ok=True)

            temp_file_path = storage_.get_join_path(temp_upload_dir, order)

            await storage_.async_write_file_wb(temp_file_path, await upload_file.read())

            if not storage_.is_file_exist(temp_file_path):
                raise HTTPException(
                    status_code=Status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error occurred during upload: File not found",
                )

            logger.success(f"successfully upload chunck : {file_id} : {order}")

            # 返回临时文件目录和文件名以备后续合并
            return {"temp_upload_dir": temp_upload_dir, "filename": order, "code": 200}

        except Exception as e:
            raise HTTPException(
                status_code=Status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error occurred during upload: {type(e)}, {str(e)}",
            )

    @app.post("/merge/")
    async def minio_merge_files(
        bucket_name: str,
        filename: str,  # is object_name
        file_id: str,
        client: Minio = Depends(get_minio_client),
    ):

        logger.debug(
            f"mergefilename: {filename}, mergefile_id: {file_id}, mergebucket_name: {bucket_name}"
        )
        found = client.bucket_exists(bucket_name)
        if not found:
            client.make_bucket(bucket_name)
            logger.debug(f"Created bucket:{bucket_name}")
        else:
            logger.debug(f"Bucket {bucket_name} already exists")

        temp_upload_dir = storage_.get_join_path(TEMP_UPLOAD_DIR, file_id)

        __set_parts = sorted(  # type: ignore
            set(storage_.get_dir_files(temp_upload_dir)),  # type: ignore
            key=lambda x: int(storage_.get_path_basename(x)),
        )
        # 找到所有分片文件
        parts: tuple[str] = tuple(__set_parts if __set_parts else [])  # type: ignore

        if len(parts) == 0:  # type: ignore
            raise HTTPException(
                status_code=Status.HTTP_404_NOT_FOUND,
                detail="No file to merge, please upload file first",
            )

        order_int_last = -1
        for part in parts:
            order = storage_.get_path_basename(part)
            print(order, part)
            order_int = int(order)
            if order_int_last > 0 and order_int - order_int_last != 1:
                logger.error(f"invalid part file: {order_int_last + 1}")
                raise HTTPException(
                    status_code=Status.HTTP_404_NOT_FOUND,
                    detail=f"missing part file: {part}",
                )
            if order_int < 0:
                logger.error(f"invalid part file: {part}")
                raise HTTPException(
                    status_code=Status.HTTP_404_NOT_FOUND,
                    detail="invalid part file",
                )
            order_int_last = order_int

        # logger.debug(f"merge file: {file_id}")

        headers: dict[str, str] = {"Content-Type": "application/octet-stream"}

        # 创建 MinIO 的分片上传会话
        upload_id = client._create_multipart_upload(  # type: ignore
            bucket_name=bucket_name,
            object_name=filename,
            headers=headers,  # type: ignore
        )

        # 逐个上传分片
        for i, part in enumerate(parts):
            part_path: str = part  # type: ignore
            if not storage_.is_file_exist(part_path):
                logger.error(f"missing part file, merge failed: {part_path}")
                raise HTTPException(
                    status_code=Status.HTTP_404_NOT_FOUND,
                    detail="missing part file, merge failed",
                )
            part_number = i + 1
            data = await storage_.async_read_file_rb(part_path)
            client._upload_part(  # type: ignore
                bucket_name=bucket_name,
                object_name=filename,
                part_number=part_number,  # 分片编号从 1 开始
                upload_id=upload_id,
                data=data,
                headers=None,
            )
            print(f"Merged part {part_path}")

        list_parts = client._list_parts(  # type: ignore
            bucket_name=bucket_name,
            object_name=filename,
            upload_id=upload_id,
        ).parts

        for p in list_parts:
            print(p.size, p.part_number)

        try:

            client._complete_multipart_upload(  # # type: ignore
                bucket_name=bucket_name,
                object_name=filename,
                upload_id=upload_id,
                parts=list_parts,
            )

            # 删除临时分片文件目录

            return {"message": "File uploaded successfully", "code": 200}
        except Exception as e:
            logger.error(f"merge failed: {type(e)}{str(e)}")
            raise HTTPException(
                status_code=Status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"merge failed: {type(e)}{str(e)}",
            )

        finally:

            storage_.remove_path(temp_upload_dir)
