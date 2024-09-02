# encoding: utf-8

# import requests
import json
from rich import print
from loguru import logger
import asyncio
from asyncio import run
from httpx import AsyncClient
import httpx
import os
from models import SessionLocal, User, File

db = SessionLocal()

# base_url = "http://47.115.43.139:8000"
# base_url = "https://whysiki.fun:8000"
base_url = "http://localhost:8000"

user_t = {"username": "whysiki", "password": "778899vvbbnnmm"}


# 注册用户
async def register_user():
    url = f"{base_url}/users/register"
    headers = {"Content-Type": "application/json"}
    data = user_t
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=json.dumps(data))
    print(response.json())

    assert db.query(User).filter(User.username == user_t["username"]).first()


run(register_user())


# 用户登录
async def login_user():
    url = f"{base_url}/users/login"
    headers = {"Content-Type": "application/json"}
    data = user_t
    async with httpx.AsyncClient() as requests:
        response = await requests.post(url, headers=headers, data=json.dumps(data))

    print(response.status_code)
    assert response.status_code == 200
    print(response.json())
    return response.json()["access_token"]


access_token = run(login_user())


# 获取当前用户信息
async def get_current_user():
    url = f"{base_url}/users/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as requests:
        response = await requests.get(url, headers=headers)
    print(response.json())
    return response.json()


# get_current_user()
run(get_current_user())


# 删除用户
async def delete_user():
    url = f"{base_url}/users/delete"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as requests:
        id = (await get_current_user())["id"]
        response = await requests.delete(url, headers=headers, params=dict(id=id))
    print(response.json())

    assert not db.query(User).filter(User.username == user_t["username"]).first()


run(delete_user())

run(register_user())
run(register_user())
access_token = run(login_user())
# get_current_user()
run(get_current_user())


# 上传文件
async def upload_file():
    url = f"{base_url}/files/upload"
    headers = {"Authorization": f"Bearer {access_token}"}
    files = {"file": open(r"D:\Backup\Videos\2024-04-15 01-31-54.mkv", "rb")}
    async with httpx.AsyncClient() as requests:
        response = await requests.post(url, headers=headers, files=files)
    print(response.json())
    assert os.path.exists(r"uploads\whysiki\mkv\2024-04-15 01-31-54.mkv")

    assert db.query(File).filter(File.filename == "2024-04-15 01-31-54.mkv").first()
    assert db.query(File).filter(File.file_owner_name == user_t["username"]).first()
    return response.json()


run(get_current_user())


# 下载文件
async def download_file():
    # upload_file()
    file_json = await upload_file()
    fire_id = file_json["id"]
    file_name = file_json["filename"]
    url = f"{base_url}/files/download"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as requests:
        response = await requests.get(
            url, headers=headers, params=dict(file_id=fire_id)
        )
    logger.debug(f"Download file: {file_name}")
    print(response.status_code)
    with open(file_name, "wb") as f:
        f.write(response.content)


# download_file()
run(download_file())


# 列出文件
async def list_files():
    url = f"{base_url}/files/list"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as requests:
        response = await requests.get(url, headers=headers)
    # print(response.json())
    files_id_name = [(d["id"], d["filename"]) for d in response.json()["files"]]
    return files_id_name


files_id_name = run(list_files())
print(files_id_name)


# 删除文件
async def delete_file(file_id: str):
    url = f"{base_url}/files/delete"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as requests:
        response = await requests.delete(
            url, headers=headers, params=dict(file_id=file_id)
        )
    print(response.json())
    assert not os.path.exists(r"uploads\whysiki\mkv\2024-04-15 01-31-54.mkv")
    assert not db.query(File).filter(File.id == file_id).first()


async def file_info(file_id: str):
    url = f"{base_url}/files/info"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as requests:
        response = await requests.get(
            url, headers=headers, params=dict(file_id=file_id)
        )
    print("File info:")
    print(response.json())


# for file_id, file_name in files_id_name:
# file_info(file_id)

# delete_file(file_id)
# print(f"Delete file: {file_name}")

# list_files()

run(upload_file())
run(get_current_user())


# 删除用户的所有文件
async def delete_user_files():
    url = f"{base_url}/users/files/delete"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as requests:
        response = await requests.delete(url, headers=headers)

    print(response.status_code)

    print(response.json())

    assert not os.path.exists(r"uploads\whysiki\mkv\2024-04-15 01-31-54.mkv")

    assert not db.query(File).filter(File.file_owner_name == user_t["username"]).first()

    assert not db.query(File).filter(File.filename == "2024-04-15 01-31-54.mkv").first()


# 重置数据库
async def reset_db(root, rootpassword):
    await upload_file()
    await get_current_user()
    url = f"{base_url}/db/reset"
    headers = {"Content-Type": "application/json"}
    data = {"username": root, "password": rootpassword}
    async with httpx.AsyncClient() as requests:
        response = await requests.post(url, headers=headers, data=json.dumps(data))
    print(response.json())
    assert not os.path.exists(r"uploads\whysiki\mkv\2024-04-15 01-31-54.mkv")


run(delete_user_files())
files_id_name = run(list_files())
print(files_id_name)
run(reset_db("whysiki", "123456789"))

if db:
    db.close()

if os.path.exists(r"2024-04-15 01-31-54.mkv"):
    os.remove(r"2024-04-15 01-31-54.mkv")


# git checkout --ours fileserver.db

# @REM source myenv/bin/activate
# @REM python3 -m venv myenv
# pip install gunicorn

# gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b :8000 main:app
"gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b :8000 --certfile=./ca/cert.crt --keyfile=./ca/private.key main:app"
"gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b :8000 --certfile=./ca/cert.crt --keyfile=./ca/private.key -D main:app"

# sudo killall gunicorn

# gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b :8000 -D main:app

# tasklist | findstr "gunicorn"

# ps aux | grep gunicorn


# cd firecloud/fastapi_filecloud_backend && source myenv/bin/activate && gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b :8000 -D main:app


{
    "id": "f6f46bb74f9687ec40c362e1cf9bd23758e7d0e5e73e9a6238cd6f9684dc3fd045c571a156ddcef41351a713bcddee5ba7e95460",
    "filename": "2024-04-15 01-31-54.mkv",
    "file_size": "1448764",
    "message": "File found",
    "file_create_time": "2024-06-02 00:42:12",
    "file_type": "mkv",
    "file_owner_name": "testuser",
    "file_path": "uploads/testuser/mkv/2024-04-15 01-31-54.mkv",
    "file_download_link": "",
}


"sudo ln -s /etc/nginx/sites-available/pccag1 /etc/nginx/sites-enabled/"
# server {
#     listen 80;
#     server_name whysiki.fun;

#     root /root/my-cloud-disk/dist;
#     index index.html;

#     location / {
#         try_files $uri $uri/ /index.html;
#     }
# }
"sudo nginx -t"
"sudo systemctl reload nginx"

# 本地分支和远程分支有分歧（divergent），
# //需要指定如何协调它们。
# 通常，你可以选择以下三种策略之一：
# git config pull.rebase false
# git config pull.rebase true
# git config pull.ff only

"""
sudo apt install nginx
sudo nano /etc/nginx/sites-available/filecloud
server {
    listen 80;
    server_name 8.138.124.53;

    location /filecloud/ {
        alias /root/firecloud/fastapi_filecloud_backend/dist/;
        autoindex on;
        try_files $uri $uri/ =404;
    }
}
sudo ln -s /etc/nginx/sites-available/filecloud /etc/nginx/sites-enabled/
sudo systemctl start nginx
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl status nginx


#!/bin/bash

# 安装 Nginx
# sudo apt update
# sudo apt install -y nginx

# 创建 Nginx 配置文件
NGINX_CONF="/etc/nginx/sites-available/filecloud"
sudo tee $NGINX_CONF > /dev/null <<EOL
server {
    listen 80;
    server_name 8.138.124.53;

root /root/firecloud/fastapi_filecloud_backend/dist;
index index.html;


    location /filecloud {
        try_files $uri $uri/ /index.html;
    }
}
EOL

# 创建符号链接以启用配置
sudo ln -s $NGINX_CONF /etc/nginx/sites-enabled/

# 启动 Nginx 服务
sudo systemctl start nginx

# 测试 Nginx 配置
sudo nginx -t

# 重新加载 Nginx 服务
sudo systemctl reload nginx
sudo systemctl restart nginx
sudo systemctl reload nginx
# 检查 Nginx 服务状态
# sudo systemctl status nginx
# 日志文件
# sudo cat /var/log/nginx/error.log

"""


"""
cat /etc/passwd
cat /etc/nginx/nginx.conf | grep user
"""
