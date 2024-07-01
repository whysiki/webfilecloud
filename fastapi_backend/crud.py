# encoding: utf-8
from sqlalchemy.orm import Session
from models import User, File, association_table
from auth import verify_password
from schemas import UserIn
from datetime import datetime
from fastapi import HTTPException
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
from storage_ import handler as storage_
from functools import lru_cache
from config.status import StatusConfig as status
from typing import Callable, Any, Tuple, List


def handle_db_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator function to handle database errors uniformly across database operations.

    Raises:

        - HTTP_500_INTERNAL_SERVER_ERROR SQLAlchemyError: Catch all SQLAlchemy errors and return a 500 Internal Server Error.

        - HTTP_500_INTERNAL_SERVER_ERROR Exception: Catch all other exceptions and return a 500 Internal Server Error.
    """

    @wraps(func)
    @lru_cache(maxsize=256)
    def wrapper(*args: Tuple[Any], **kwargs: dict[str, Any]) -> Any:
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error occurred",
            )
        except HTTPException as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise e
        except Exception as e:
            logger.warning(f"Unexpected error in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{type(e)}:{str(e)}",
            )

    return wrapper


# 获取文件列表
@handle_db_errors
def get_file_id_list(db: Session, user: User) -> List[str]:
    """
    Raises:

        - HTTP_404_NOT_FOUND: If the user is not found, raises HTTP 404 Not Found.

        - HTTP_500_INTERNAL_SERVER_ERROR: If any other error occurs, raises HTTP 500 Internal Server Error.
    """
    db_user = db.query(User).filter(User.id == user.id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user.id} not found",
        )

    file_id_list = [file.id for file in db_user.files]
    return file_id_list


# 获取文件对象通过文件ID
@handle_db_errors
def get_file_by_id(db: Session, file_id: str) -> File:
    """
    Raises:

        - HTTP_404_NOT_FOUND:

        - HTTP_500_INTERNAL_SERVER_ERROR: If any other error occurs, raises HTTP 500 Internal Server Error.
    """
    f = db.query(File).filter(File.id == file_id).first()
    if not f:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    return f


# 获取文件对象通过文件名
@handle_db_errors
def get_file_by_filename(db: Session, filename: str) -> File:
    """
    Raises:

        - HTTP_404_NOT_FOUND:

        - HTTP_500_INTERNAL_SERVER_ERROR: If any other error occurs, raises HTTP 500 Internal Server Error.
    """
    f = db.query(File).filter(File.filename == filename).first()
    if not f:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    return f


# 添加用户到数据库
@handle_db_errors
def add_user(db: Session, user: User) -> User:
    """
    add user to the database

    Raises:

        - HTTP_500_INTERNAL_SERVER_ERROR: If any other error occurs, raises HTTP 500 Internal Server Error.
    """
    user.register_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # type: ignore
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.success(f"Added an user : {user.username}")
    return user


@handle_db_errors
def delete_file_from_db(db: Session, file: File) -> None:
    """
    delete file from the database

    Raises:

        HTTP_500_INTERNAL_SERVER_ERROR: If any other error occurs, raises HTTP 500 Internal Server Error.
    """

    if bool(file.file_owner_name):
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
            # 一个文件路径可能对应多个文件id
            # 只有当前文件链接到文件路径才删除（即文件路径对应的文件id只有当前要删除的文件）
            if (storage_.is_file_exist(file.file_path)) and (  # type: ignore
                # only current file link to the file path
                len(db.query(File).filter(File.file_path == file.file_path).all())
                == 1
            ):
                storage_.remove_file(file.file_path)  # type: ignore # Now delete the file
                logger.warning(f"Deleted a file: {file.filename}")
            else:
                logger.error("File not found in the store")
            db.commit()  # Commit all changes including cascade deletions

        else:
            logger.error("File not associated with the user")
    else:
        logger.error("File owner not defined")


# 从数据库删除用户, 同时删除用户下面所有文件
@handle_db_errors
def delete_user_from_db(db: Session, user: User) -> None:
    """
    Raises:
        HTTP_500_INTERNAL_SERVER_ERROR if any other error occurs.
    """

    user_files = db.query(File).filter(File.file_owner_name == user.username).all()

    # delete files from the store
    for file in user_files:
        if (
            storage_.is_file_exist(file.file_path)  # type: ignore
            # and len(db.query(File).filter(File.file_path == file.file_path ).all()) == 1
        ):
            storage_.remove_file(file.file_path)  # type: ignore
            logger.warning(f"Deleted a file: {file.filename}")
        else:
            # print(storage_.is_file_exist(file.file_path))
            logger.error(f"File not found in the store : {file.file_path}")

    db.query(association_table).filter(
        association_table.c.user_id == user.id
    ).delete()  # 删除用户和文件的关联记录
    db.query(File).filter(
        File.file_owner_name == user.username
    ).delete()  # 删除File表中用户的所有文件记录
    db.delete(user)
    db.commit()
    logger.warning(f"Deleted an user : {user.username}")


# 获取用户通过用户名
@handle_db_errors
def get_user_by_username(db: Session, username: str) -> User:
    """

    will automatically authenticate the user if the user is found.

    if not found, will raise HTTP 404 Not Found.

    Raises:
        - HTTP_404_NOT_FOUND: If the user is not found, raises HTTP 404 Not Found.

        - HTTP_500_INTERNAL_SERVER_ERROR: If any other error occurs, raises HTTP 500 Internal Server Error.
    """
    u = db.query(User).filter(User.username == username).first()
    if not u:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return u


# 通过ID获取用户
@handle_db_errors
def get_user_by_id(db: Session, id: str) -> User:
    """
    Raises:
        - HTTP_404_NOT_FOUND if the user is not found.

        - HTTP_500_INTERNAL_SERVER_ERROR if any other error occurs.
    """
    u = db.query(User).filter(User.id == id).first()
    if not u:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return u


# 检查用户名是否存在
@handle_db_errors
def is_user_exist(db: Session, username: str) -> bool:
    """
    Raises:
        - HTTP_500_INTERNAL_SERVER_ERROR if any other error occurs.
    """
    return db.query(User).filter(User.username == username).first() is not None


# 检查用户是否合法, 用户名和密码是否匹配
@handle_db_errors
def is_not_valid_user(db: Session, userin: UserIn) -> bool:
    """
    Raises:
        - HTTP_500_INTERNAL_SERVER_ERROR if any other error occurs.
        - HTTP_404_NOT_FOUND: If the user is not found, raises HTTP 404 Not Found.
    """
    user = get_user_by_username(db, userin.username)
    return not user or not verify_password(userin.password, user.password)


@handle_db_errors
def add_file_id_to_user(db: Session, user: User, file_id: str) -> None:
    """
    Raises:
        - HTTP_500_INTERNAL_SERVER_ERROR if any other error occurs.
    """
    file = get_file_by_id(db, file_id)
    user.files.append(file)
    db.add(file)
    db.commit()
    logger.success(f"Added a file to user : {user.username}")


@handle_db_errors
def is_file_in_user_files(db: Session, user: User, file: File) -> bool:
    """
    Raises:
        - HTTP_500_INTERNAL_SERVER_ERROR if any other error occurs.
    """
    return file in user.files


@handle_db_errors
def is_fileid_in_user_files(db: Session, user: User, file_id: str) -> bool:
    """
    Raises:
        - HTTP_500_INTERNAL_SERVER_ERROR if any other error occurs.
    """
    file = get_file_by_id(db, file_id)
    return file in user.files


@handle_db_errors
def is_user_files_empty(db: Session, user: User) -> bool:
    """
    Raises:
        - HTTP_500_INTERNAL_SERVER_ERROR if any other error occurs.
    """
    f = (
        db.query(association_table)
        .filter(association_table.c.user_id == user.id)
        .first()
    )
    if f:
        logger.warning("not empty user files")
    return False if f else True


@handle_db_errors
def add_file_to_user(db: Session, file: File, user: User) -> User:
    """
    Raises:
        - HTTP_500_INTERNAL_SERVER_ERROR if any other error occurs.
    """
    user.files.append(file)
    db.add(file)
    db.commit()
    logger.success(f"Added a file to user : {user.username}")
    return user


@handle_db_errors
def modify_file_attributes(db: Session, file: File, arrtibute: str, value: str) -> None:
    """
    Raises:
        - HTTP_500_INTERNAL_SERVER_ERROR if any other error occurs.
    """
    setattr(file, arrtibute, value)
    db.commit()
    logger.success(f"Modified file attribute : {arrtibute} to {value}")
