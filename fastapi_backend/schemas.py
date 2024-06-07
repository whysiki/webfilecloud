# encoding: utf-8

from pydantic import BaseModel, Field

# from typing import Set


# 用户输入模型, Pydantic 模型
class UserIn(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, title="username")
    password: str = Field(..., min_length=8, max_length=100, title="password")


# 用户输出模型, Pydantic 模型
class UserOut(BaseModel):
    message: str
    id: str = Field("", title="id")  # 设置默认值
    username: str


class UserShow(BaseModel):
    username: str
    register_time: str
    files: list[str] = Field(default_factory=list)
    id: str
    message: str


# 文件输入模型, Pydantic 模型
class Token(BaseModel):
    access_token: str
    token_type: str


# 文件模型, SQLAlchemy 模型
# 文件模型, SQLAlchemy 模型
class FileOut(BaseModel):
    id: str
    filename: str
    file_size: str
    message: str
    file_create_time: str
    file_type: str
    file_owner_name: str
    file_path: str = Field("", title="file_path")  # 设置默认值
    file_download_link: str = Field("", title="file_download_link")  # 设置默认值
    # 默认为空
    file_nodes: list[str] = Field(default_factory=list)


class FileList(BaseModel):
    files: list[FileOut]


class DbOut(BaseModel):
    message: str
    user_count: int
    file_count: int
    # total_size: str
    user_list: list[UserShow] = Field(default_factory=list)
    file_list: list[FileOut] = Field(default_factory=list)


# class FileNodes(BaseModel):
# file_nodes: list[str] = Field(default_factory=list)
