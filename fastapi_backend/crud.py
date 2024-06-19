# encoding: utf-8
from sqlalchemy.orm import Session
from models import User, File, association_table
from auth import verify_password
from schemas import UserIn
from datetime import datetime
import os
from fastapi import HTTPException
from loguru import logger
from config import Config
import shutil
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps


def handle_db_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error occurred")
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=404, detail=f"{str(e)}")  # ,type；{type(e)}

    return wrapper


# 获取文件列表
@handle_db_errors
def get_file_id_list(db: Session, user: User) -> list:
    db_user = db.query(User).get(user.id)
    file_id_list = [file.id for file in db_user.files]
    return file_id_list


# 获取文件对象通过文件ID
@handle_db_errors
def get_file_by_id(db: Session, file_id: str) -> File:
    # logger.debug(f"file_id: {file_id}")
    f = db.query(File).filter(File.id == file_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="File not found")
    return f


# 获取文件对象通过文件名
@handle_db_errors
def get_file_by_filename(db: Session, filename: str) -> File:
    f = db.query(File).filter(File.filename == filename).first()
    if not f:
        raise HTTPException(status_code=404, detail="File not found")
    return f


# 添加用户到数据库
@handle_db_errors
def add_user(db: Session, user: User) -> User:
    user.register_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.add(user)
    db.commit()
    db.refresh(user)
    assert (
        db.query(User).filter(User.username == user.username).first()
    ), "Add user failed"
    logger.success(f"Added an user : {user.username}")
    return user


@handle_db_errors
def delete_file_from_db(db: Session, file: File) -> None:
    if file.file_owner_name:
        username = file.file_owner_name
        user = get_user_by_username(db, username)
        if file in user.files:
            f = db.query(association_table).filter(
                association_table.c.file_id == file.id
            )
            if f:
                f.delete()
                db.commit()
            if file in user.files:
                user.files.remove(file)
                db.commit()
            db.delete(file)  # 删除文件在File表中的记录
            db.commit()  # Commit all changes including cascade deletions
            if os.path.exists(file.file_path):
                os.remove(file.file_path)  # Now delete the file
                logger.debug(f"Deleted a file: {file.filename}")
            else:
                logger.error("File not found in the filesystem")
            # test 开发时使用, 用于检查文件是否被删除 生产环境不需要
            assert not os.path.exists(file.file_path), "File still exists"
            if file.file_owner_name:
                username = file.file_owner_name
                user = get_user_by_username(db, username)
                assert file not in user.files, "file in user.files"
                assert (
                    not db.query(File).filter(File.id == file.id).first()
                ), "file in File table"
            db.commit()
            # test
        else:
            logger.error("File not associated with the user")
    else:
        logger.error("File owner not defined")


# 从数据库删除用户, 同时删除用户下面所有文件
@handle_db_errors
def delete_user_from_db(db: Session, user: User) -> None:
    db.query(association_table).filter(
        association_table.c.user_id == user.id
    ).delete()  # 删除用户和文件的关联记录
    db.query(File).filter(
        File.file_owner_name == user.username
    ).delete()  # 删除File表中用户的所有文件记录
    db.delete(user)
    db.commit()
    assert (
        not db.query(User).filter(User.username == user.username).first()
    ), "User in User table"
    assert (
        not db.query(association_table)
        .filter(association_table.c.user_id == user.id)
        .first()
    ), "User in association table"
    assert (
        not db.query(File).filter(File.file_owner_name == user.username).first()
    ), "User in File table"

    # 删除用户文件夹
    user_folder = os.path.join(Config.UPLOAD_PATH, user.username)
    if os.path.exists(user_folder):
        shutil.rmtree(user_folder)
    logger.debug(f"Deleted an user : {user.username}")


# 获取用户通过用户名
@handle_db_errors
def get_user_by_username(db: Session, username: str) -> User:
    u = db.query(User).filter(User.username == username).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return u


# 通过ID获取用户
@handle_db_errors
def get_user_by_id(db: Session, id: str) -> User:
    u = db.query(User).filter(User.id == id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return u


# 检查用户名是否存在
@handle_db_errors
def is_user_exist(db: Session, username: str) -> bool:
    return db.query(User).filter(User.username == username).first() is not None


# 检查用户是否合法, 用户名和密码是否匹配
@handle_db_errors
def is_not_valid_user(db: Session, userin: UserIn) -> bool:
    user = get_user_by_username(db, userin.username)
    return not user or not verify_password(userin.password, user.password)


@handle_db_errors
def add_file_id_to_user(db: Session, user: User, file_id: str) -> None:
    file = get_file_by_id(db, file_id)
    user.files.append(file)
    db.commit()
    assert file in user.files, "Add file to user failed"
    logger.success(f"Added a file to user : {user.username}")


@handle_db_errors
def is_file_in_user_files(db: Session, user: User, file: File) -> bool:
    return file in user.files


@handle_db_errors
def is_fileid_in_user_files(db: Session, user: User, file_id: str) -> bool:
    file = get_file_by_id(db, file_id)
    return file in user.files


@handle_db_errors
def is_user_files_empty(db: Session, user: User) -> bool:
    f = (
        db.query(association_table)
        .filter(association_table.c.user_id == user.id)
        .first()
    )
    if f:
        logger.warning("not empty user files")
        # logger.debug()
    return False if f else True


@handle_db_errors
def add_file_to_user(db: Session, file: File, user: User) -> User:
    user.files.append(file)
    db.commit()
    assert file in user.files, "Add file to user failed"
    logger.success(f"Added a file to user : {user.username}")
    return user



@handle_db_errors
def modify_file_attributes(db: Session, file: File, arrtibute: str, value: str) -> None:
    setattr(file, arrtibute, value)
    db.commit()
    assert getattr(file, arrtibute) == value, "Modify file attribute failed"
    logger.success(f"Modified file attribute : {arrtibute} to {value}")
