# encoding: utf-8
from fastapi import HTTPException, Depends
from uuid import uuid4
from starlette.requests import Request
from sqlalchemy.orm import Session
import models  # model definition
import schemas
import crud  # database operations
from auth import pwd_context, create_access_token, get_current_username
from fastapi import File, UploadFile
from datetime import datetime, timedelta

# from fastapi import Header
from typing import Optional

# import auth  # authentication functions
from fastapi.responses import FileResponse
import hashlib
import config  # costom configuration
from fastapi.responses import StreamingResponse
import aiofiles
from loguru import logger
from dep import get_db, get_access_token, get_current_userneame  # inject dependency
from app import app  # fast app instance
import json
import numpy
import utility  # costom utility functions
from concurrent.futures import ThreadPoolExecutor
import io
import asyncio
from urllib.parse import quote
import mimetypes
import storage_  # costom storage functions


# register user
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


# login user and return access_token and refresh_token
@app.post("/users/login", response_model=schemas.Token)
async def login_user_token(user_in: schemas.UserIn, db: Session = Depends(get_db)):
    if crud.is_not_valid_user(db, user_in):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token(data={"sub": user_in.username})
    refresh_token = create_access_token(
        data={"sub": user_in.username},
        expires_delta=timedelta(minutes=config.Config.ACCESS_TOKEN_EXPIRE_MINUTES * 2),
    )
    return schemas.Token(
        access_token=access_token, token_type="bearer", refresh_token=refresh_token
    )


# update access_token with refresh_token
@app.post("/users/refresh", response_model=schemas.Token)
async def refresh_token(access_token: str = Depends(get_access_token)):
    username: str = get_current_username(access_token)
    ## by leveraging the refresh token, the user can get a new access token
    access_token = create_access_token(data={"sub": username})
    refresh_token = create_access_token(
        data={"sub": username},
        expires_delta=timedelta(minutes=config.Config.ACCESS_TOKEN_EXPIRE_MINUTES * 2),
    )
    test_username = get_current_username(access_token)
    test_username_refresh = get_current_username(refresh_token)
    if not (test_username == username == test_username_refresh):
        raise HTTPException(status_code=401, detail="refresh token failed")
    logger.debug(f"refresh token :{refresh_token}")
    return schemas.Token(
        access_token=access_token, token_type="bearer", refresh_token=refresh_token
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
    if not (user.username == current_username):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    crud.delete_user_from_db(db, user)

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
        raise HTTPException(status_code=401, detail="Invalid username or password")

    username: str = get_current_username(access_token)

    if username != user_in.username:

        raise HTTPException(status_code=401, detail="Invalid username or password")

    user = crud.get_user_by_username(db, username)

    return schemas.UserOut(id=user.id, username=user.username, message="User found.")


# get user info
@app.post("/users/me", response_model=schemas.UserShow)
async def read_users_me(
    user_in: schemas.UserIn,
    access_token: str = Depends(get_access_token),
    db: Session = Depends(get_db),
):
    if crud.is_not_valid_user(db, user_in):
        raise HTTPException(status_code=401, detail="Invalid username or password")

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
        raise HTTPException(status_code=500, detail="Delete files failed")
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
            logger.warning(f"file_id: {file_id} already exists, upload failed")
            filem = crud.get_file_by_id(db, file_id=file_id)
            if storage_.is_file_exist(filem.file_path):
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

    ## I forgot to store the same files at design time 😅😅.
    # It doesn't matter if you don't store large files for your own  use 🤣
    ## It should be necessary to directly compute the hash of the file contents as the file id, if present in the file table
    # Then check if the file is for the current user and if it is, return it exists
    # If not, add this file in the file relationship above the new user,  and then return ## Forgot the same file redundancy problem at design time 😅😅,  and don't store large files for your own use, it doesn't matter 🤣
    ## It should be necessary to directly compute the hash of the file contents as the file id, if present in the file table
    # Then check if the file is for the current user and if it is, return it exists
    # If not, add the file to the new user's file relationship and return
    file_content: bytes = await file.read()
    # the file content hash + the user name hash + the file node hash 🤣
    file_hash = (
        hashlib.sha256(file_content).hexdigest()
        + hashlib.sha1(username.encode()).hexdigest()
        + hashlib.sha1("".join(file_nodes).encode()).hexdigest()
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

    ##

    filename = file.filename

    filename = storage_.get_path_basename(filename)

    file_type = filename.split(".")[-1] if "." in filename else "binary"

    file_path = utility.get_new_path(
        storage_.get_join_path(config.Config.UPLOAD_PATH, username, file_type, filename)
    )

    storage_.makedirs(file_path)

    await storage_.async_write_file_wb(file_path, file_content)

    file_size = str(storage_.get_file_size(file_path))
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

        raise HTTPException(status_code=403, detail="Permission denied")

    if not crud.is_fileid_in_user_files(db, user, file.id):

        raise HTTPException(
            status_code=404, detail="File not found in user's file list"
        )

    if not storage_.is_file_exist(file.file_path):

        raise HTTPException(status_code=404, detail="File path not found")

    logger.debug(f"Download file: {file.file_path}")

    return FileResponse(
        file.file_path,
        media_type="application/octet-stream",
        filename=storage_.get_path_basename(file.file_path),
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
        raise HTTPException(status_code=403, detail="Permission denied")

    if not crud.is_fileid_in_user_files(db, user, file.id):
        raise HTTPException(
            status_code=404, detail="File not found in user's file list"
        )

    if not storage_.is_file_exist(file.file_path):
        raise HTTPException(status_code=404, detail="File path not found")

    file_size = storage_.get_file_size(file.file_path)
    range_header = request.headers.get("Range")
    start, end = utility.get_start_end_from_range_header(range_header, file_size)

    return StreamingResponse(
        utility.file_iterator(file.file_path, start, end),
        status_code=206 if range_header else 200,
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

    if file.file_owner_name != user.username:

        raise HTTPException(status_code=403, detail="Permission denied")

    if not crud.is_file_in_user_files(db, user, file):

        raise HTTPException(
            status_code=404, detail="File not found in user's file list"
        )

    if not storage_.is_file_exist(file.file_path):

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


# reset database, dangerous api, not recommended for production
@app.post("/db/reset", response_model=schemas.DbOut)
async def reset_db(user_in: schemas.UserIn, db: Session = Depends(get_db)):
    if (
        user_in.username != config.Config.ROOT_USER
        or user_in.password != config.Config.ROOT_PASSWORD
    ):
        raise HTTPException(status_code=403, detail="Permission denied")
    db.query(models.association_table).delete()
    db.query(models.User).delete()
    db.query(models.File).delete()
    db.commit()

    storage_.remove_path(config.Config.UPLOAD_PATH)
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
        raise HTTPException(status_code=405, detail="Invalid file name")

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

        raise HTTPException(status_code=403, detail="Permission denied")

    if not crud.is_file_in_user_files(db, user, file):

        raise HTTPException(
            status_code=404, detail="File not found in user's file list"
        )

    # if not storage_.is_file_exist(file.file_path):
    if not storage_.is_file_exist(file.file_path):

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


# modify file nodes
@app.post("/file/modifynodes", response_model=schemas.FileOut)
async def modify_file_nodes(
    file_id: str,
    file_nodes: Optional[str] = None,
    access_token: str = Depends(get_access_token),
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


# direct download file, direct link, actually may need to generate a temporary link, to be optimized
@app.get("/file/directdownload/{user_id}/{file_id}/{file_name}")
async def download_file(
    user_id: str, file_id: str, file_name: str, db: Session = Depends(get_db)
):
    user = crud.get_user_by_id(db, user_id)
    file = crud.get_file_by_id(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    if file.file_owner_name != user.username or file.filename != file_name:
        raise HTTPException(status_code=403, detail="Permission denied")

    file_size = storage_.get_file_size(file.file_path)

    return FileResponse(
        file.file_path,
        filename=file.filename,
        media_type="application/octet-stream",
        headers={"Content-Length": str(file_size)},
    )


# download file with stream response
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

    # if not storage_.is_file_exist(file.file_path):
    if not storage_.is_file_exist(file.file_path):
        raise HTTPException(status_code=404, detail="File path not found")

    # file_size = storage_.get_file_size(file.file_path)
    file_size = storage_.get_file_size(file.file_path)
    range_header = request.headers.get("Range")

    start, end = utility.get_start_end_from_range_header(range_header, file_size)

    return StreamingResponse(
        utility.file_iterator(file.file_path, start, end),
        status_code=206 if range_header else 200,
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
            status_code=400,
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
        if storage_.is_file_exist(config.User.DEFAULT_PROFILE_IMAGE):
            user.profile_image = config.User.DEFAULT_PROFILE_IMAGE
            logger.warning("default profile_image")
        else:
            raise HTTPException(
                status_code=404,
                detail="Profile image not found, Server error, no default profile image",
            )

    return FileResponse(
        user.profile_image,
        filename=storage_.get_path_basename(user.profile_image),
        media_type="application/octet-stream",
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
        raise HTTPException(status_code=404, detail="User not found")

    # save profile image
    file_path = utility.get_new_path(
        storage_.get_join_path(
            config.Config.STATIC_PATH, username, "profile", file.filename
        )
    )
    storage_.makedirs(file_path)
    try:
        total_size = 0
        async with aiofiles.open(file_path, "wb") as buffer:
            while True:
                chunk = await file.read(1024)  # read in 1KB chunks
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > config.User.PROFILE_IMAGE_MAX_FILE_SIZE:
                    storage_.remove_file(file_path)  # remove the file
                    logger.warning("profile image File size exceeds maximum limit")
                    raise HTTPException(
                        status_code=400,
                        detail="profile image File size exceeds maximum limit",
                    )
                await buffer.write(chunk)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Profile image save failed, Server error: {e}"
        )

    user.profile_image = file_path

    db.commit()

    if not user.profile_image or not storage_.is_file_exist(user.profile_image):
        raise HTTPException(
            status_code=500, detail="Profile image upload failed, Server error"
        )

    return schemas.UserOut(
        # id=user.id,
        username=user.username,
        profile_image=user.profile_image,
        message="Profile image uploaded successfully",
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
        raise HTTPException(status_code=403, detail="Permission denied")

    if not crud.is_fileid_in_user_files(db, user, file.id):
        raise HTTPException(
            status_code=404, detail="File not found in user's file list"
        )

    file.file_preview_path = storage_.get_join_path(
        config.File.PREVIEW_FILES_PATH, f"{file.id}_preview.{file.file_type}"
    )

    if (
        not file.file_preview_path
        or not storage_.is_file_exist(file.file_preview_path)
        or storage_.get_file_size(file.file_preview_path) < 100
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
        raise HTTPException(status_code=403, detail="Permission denied")

    if not crud.is_fileid_in_user_files(db, user, file.id):
        raise HTTPException(
            status_code=404, detail="File not found in user's file list"
        )

    if (
        not file.file_preview_path
        or not storage_.is_file_exist(file.file_preview_path)
        or storage_.get_file_size(file.file_preview_path) < 100
    ):

        logger.debug(f"generate preview video :{file.filename}")

        file.file_preview_path = storage_.get_join_path(
            config.File.PREVIEW_FILES_PATH, f"{file.id}_preview.mp4"
        )
        storage_.makedirs(file.file_preview_path, is_file=True)
        utility.generate_preview_video(file.file_path, file.file_preview_path)

        db.commit()

    mime_type = "video/mp4"

    filename = quote(storage_.get_path_basename(file.file_path).replace(".", "_"))

    if (
        storage_.is_file_exist(file.file_preview_path)
        and storage_.get_file_size(file.file_preview_path) > 0
    ):
        return FileResponse(
            file.file_preview_path,
            media_type=mime_type,
            headers={
                "Content-Disposition": f"attachment; filename=preview_{filename}.mp4"
            },
        )
    else:
        raise HTTPException(
            status_code=500, detail="Error: Preview file not found or empty"
        )


# get hls m3u8 file
@app.get("/file/video/{file_id}/index.m3u8")
async def get_hls_m3u8_list(file_id: str, db: Session = Depends(get_db)):

    file = crud.get_file_by_id(db, file_id)

    segment_index_path = storage_.get_join_path(config.File.M3U8_INDEX_PATH, file.id)

    index_m3u8_name = "index.m3u8"

    index_m3u8_path = storage_.get_join_path(segment_index_path, index_m3u8_name)

    try:
        utility.generate_hls_playlist(
            file.file_path,
            output_dir=segment_index_path,
            playlist_name=index_m3u8_name,
            file_id=file.id,
        )

    except Exception as e:

        logger.warning(f"{type(e)}{str(e)}")

        raise HTTPException(
            status_code=500, detail="Failed to generate HLS playlist and segments"
        )

    return FileResponse(index_m3u8_path, media_type="application/vnd.apple.mpegurl")


# get hls m3u8 segment file
@app.get("/file/segments/{file_id}/{segment_name}")
async def get_segment(request: Request, file_id: str, segment_name: str):
    segment_path = storage_.get_join_path(
        f"{storage_.get_join_path(config.File.M3U8_INDEX_PATH, file_id)}", segment_name
    )
    if not storage_.is_file_exist(segment_path):
        raise HTTPException(status_code=404, detail="Segment not found")

    file_size = storage_.get_file_size(segment_path)

    range_header = request.headers.get("Range")

    start, end = utility.get_start_end_from_range_header(range_header, file_size)

    return StreamingResponse(
        utility.file_iterator(segment_path, start, end),
        status_code=206 if range_header else 200,
        headers={
            "Content-Length": str(end - start + 1),
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
        },
    )
