
# # encoding: utf-8

# import requests
# import json
# from rich import print
# from dotenv import load_dotenv
# import os

# load_dotenv()

# startport = os.getenv("START_PORT")

# # assert startport, "error: START_PORT is None"

# root_user = os.getenv("ROOT_USER")

# root_password = os.getenv("ROOT_PASSWORD")

# # assert root_user and root_password, "error: ROOT_USER or ROOT_PASSWORD is None"

# if not startport:

#     startport = input("Please input the start port: ")

# if not root_user:
#     root_user = input("Please input the root user: ")

# if not root_password:
#     root_password = input("Please input the root password: ")

# user_t = {"username": "whysiki", "password": "123456789"}
# base_url = f"http://localhost:{startport}"

# test_file = "testfiles/1.txt"
# if not os.path.exists(test_file):
#     os.makedirs(os.path.dirname(test_file), exist_ok=True)
#     with open(test_file, "w") as f:
#         f.write("test file" * 1000)


# # 注册用户
# def register_user():
#     url = f"{base_url}/users/register"
#     headers = {"Content-Type": "application/json"}
#     data = user_t
#     response = requests.post(url, headers=headers, data=json.dumps(data))
#     print(response.json())


# register_user()


# # 用户登录
# def login_user():
#     url = f"{base_url}/users/login"
#     headers = {"Content-Type": "application/json"}
#     data = user_t
#     response = requests.post(url, headers=headers, data=json.dumps(data))

#     print(response.status_code)
#     # assert response.status_code == 200
#     print(response.json())
#     return response.json()["access_token"]


# # login_user()
# access_token = login_user()  # + "123"


# # 获取当前用户信息
# def get_current_user():
#     print("获取当前用户信息......")
#     url = f"{base_url}/users/me"
#     headers = {"Authorization": f"Bearer {access_token}"}
#     data = user_t
#     response = requests.post(url, headers=headers, data=json.dumps(data))
#     print(response.json())
#     return response.json()


# get_current_user()


# # 删除用户
# def delete_user():
#     url = f"{base_url}/users/delete"
#     headers = {"Authorization": f"Bearer {access_token}"}
#     response = requests.delete(
#         url, headers=headers, params=dict(id=get_current_user()["id"])
#     )
#     print(response.json())


# delete_user()
# register_user()
# access_token = login_user()  # + "123"
# get_current_user()


# # 上传文件
# def upload_file():
#     url = f"{base_url}/files/upload"
#     headers = {"Authorization": f"Bearer {access_token}"}
#     files = {"file": open(test_file, "rb")}
#     response = requests.post(url, headers=headers, files=files)
#     print(response.json())
#     return response.json()


# # 下载文件
# def download_file():
#     # upload_file()
#     file_json = upload_file()
#     fire_id = file_json["id"]
#     file_name = file_json["filename"]
#     url = f"{base_url}/files/download"
#     headers = {"Authorization": f"Bearer {access_token}"}
#     response = requests.get(url, headers=headers, params=dict(file_id=fire_id))
#     print(response.status_code)
#     # print(response.json())
#     with open(file_name, "wb") as f:
#         f.write(response.content)


# download_file()


# # 列出文件
# def list_files():
#     url = f"{base_url}/files/list"
#     headers = {"Authorization": f"Bearer {access_token}"}
#     response = requests.get(url, headers=headers)
#     # print(response.json())
#     files_id_name = [(d["id"], d["filename"]) for d in response.json()["files"]]
#     return files_id_name


# files_id_name = list_files()
# print(files_id_name)


# # 删除文件
# def delete_file(file_id: str):
#     url = f"{base_url}/files/delete"
#     headers = {"Authorization": f"Bearer {access_token}"}
#     response = requests.delete(url, headers=headers, params=dict(file_id=file_id))
#     print(response.json())


# def file_info(file_id: str):
#     url = f"{base_url}/files/info"
#     headers = {"Authorization": f"Bearer {access_token}"}
#     response = requests.get(url, headers=headers, params=dict(file_id=file_id))
#     # print(response.json())


# for file_id, file_name in files_id_name:
#     file_info(file_id)
#     delete_file(file_id)
#     print(f"Delete file: {file_name}")

# list_files()
# download_file()


# # 删除用户的所有文件
# def delete_user_files():
#     url = f"{base_url}/users/files/delete"
#     headers = {"Authorization": f"Bearer {access_token}"}
#     response = requests.delete(url, headers=headers)

#     print(response.status_code)

#     print(response.json())


# delete_user_files()
# files_id_name = list_files()
# print(files_id_name)


# # 重置数据库
# def reset_db(root, rootpassword):
#     url = f"{base_url}/db/reset"
#     headers = {"Content-Type": "application/json"}
#     data = {"username": root, "password": rootpassword}
#     response = requests.post(url, headers=headers, data=json.dumps(data))
#     assert response.status_code == 200, "error: reset_db failed"
#     print(response.json())


# if __name__ == "__main__":
#     pass
#     # # git checkout --ours fileserver.db

#     # # @REM source myenv/bin/activate
#     # # @REM python3 -m venv myenv

#     # # reset_db("whysiki", "123456789")

#     # reset_db(root_user, root_password)

#     # if os.path.exists(os.path.basename(test_file)):
#     #     os.remove(os.path.basename(test_file))

#     # # pip install gunicorn

#     # # gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b :8000 main:app
#     # "gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b :8000 --certfile=./ca/cert.crt --keyfile=./ca/private.key main:app"
#     # "gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b :8000 --certfile=./ca/cert.crt --keyfile=./ca/private.key -D main:app"

#     # # sudo killall gunicorn

#     # # gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b :8000 -D main:app

#     # # tasklist | findstr "gunicorn"

#     # # ps aux | grep gunicorn

#     # # cd firecloud/fastapi_filecloud_backend && source myenv/bin/activate && gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b :8000 -D main:app

#     # {
#     #     "id": "f6f46bb74f9687ec40c362e1cf9bd23758e7d0e5e73e9a6238cd6f9684dc3fd045c571a156ddcef41351a713bcddee5ba7e95460",
#     #     "filename": "2024-04-15 01-31-54.mkv",
#     #     "file_size": "1448764",
#     #     "message": "File found",
#     #     "file_create_time": "2024-06-02 00:42:12",
#     #     "file_type": "mkv",
#     #     "file_owner_name": "testuser",
#     #     "file_path": "uploads/testuser/mkv/2024-04-15 01-31-54.mkv",
#     #     "file_download_link": "",
#     # }

#     # "sudo ln -s /etc/nginx/sites-available/whysiki.fun /etc/nginx/sites-enabled/"
#     # # server {
#     # #     listen 80;
#     # #     server_name whysiki.fun;

#     # #     root /root/my-cloud-disk/dist;
#     # #     index index.html;

#     # #     location / {
#     # #         try_files $uri $uri/ /index.html;
#     # #     }
#     # # }
#     # "sudo nginx -t"
#     # "sudo systemctl reload nginx"

#     # # 本地分支和远程分支有分歧（divergent），
#     # # //需要指定如何协调它们。
#     # # 通常，你可以选择以下三种策略之一：
#     # # git config pull.rebase false
#     # # git config pull.rebase true
#     # # git config pull.ff only
