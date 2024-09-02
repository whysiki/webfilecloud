# encoding: utf-8

from typing import Any, Type
from pydantic import BaseModel, Field


def make_hashable(cls: Type[Any]) -> Type[Any]:
    def __hash__(self: Type[Any]) -> int:
        return hash((type(self),) + tuple(self.__dict__.values()))

    def __eq__(self: Type[Any], other: Type[Any]) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    if "__hash__" not in cls.__dict__:
        setattr(cls, "__hash__", __hash__)
    if "__eq__" not in cls.__dict__:
        setattr(cls, "__eq__", __eq__)
    return cls


# 用户输入模型, Pydantic 模型
@make_hashable
class UserIn(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, title="username")
    password: str = Field(..., min_length=8, max_length=100, title="password")


# 用户输出模型, Pydantic 模型
@make_hashable
class UserOut(BaseModel):
    message: str
    id: str = Field("", title="id")  # 设置默认值
    username: str
    profile_image: str = Field("", title="profile_image")  # 设置默认值
    profile: str = Field("", title="profile")  # 设置默认值
    role: str = Field("", title="role")  # 设置默认值


@make_hashable
class UserShow(BaseModel):
    username: str
    register_time: str
    files: list[str] = Field(default_factory=list)
    id: str
    message: str


# 文件输入模型, Pydantic 模型
@make_hashable
class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str = Field("", title="refresh_token")


# 文件模型, SQLAlchemy 模型
# 文件模型, SQLAlchemy 模型
@make_hashable
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


@make_hashable
class FileList(BaseModel):
    files: list[FileOut]


@make_hashable
class DbOut(BaseModel):
    message: str
    user_count: int
    file_count: int
    # total_size: str
    user_list: list[UserShow] = Field(default_factory=list)
    file_list: list[FileOut] = Field(default_factory=list)


# class FileNodes(BaseModel):
# file_nodes: list[str] = Field(default_factory=list)
