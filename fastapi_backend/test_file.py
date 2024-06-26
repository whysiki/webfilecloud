# encoding: utf-8
import asyncio
import httpx
import json
from rich import print
from rich.console import Console
from rich.prompt import Prompt
import functools
from dotenv import load_dotenv
import os
import aiofiles
from uuid import uuid4
from pathlib import Path
from PIL import Image
import cv2
import config
import random
import shutil
import re
from tqdm import tqdm
from httpx import AsyncClient
from urllib.parse import unquote
import numpy as np
from tools.testtools import (
    generate_random_image,
    generate_random_video,
    get_new_path,
    handle_error,
)

load_dotenv()

startport = os.getenv("START_PORT")

root_user = os.getenv("ROOT_USER")
root_password = os.getenv("ROOT_PASSWORD")

if not startport:
    startport = Prompt.ask("Please input the start port: ", default="8000")

if not root_user:
    root_user = input("Please input the root user: ")

if not root_password:
    root_password = input("Please input the root password: ")

while True:
    is_delete_db_test = Prompt.ask(
        "Do you want to delete the test database after the test? (yes/no): ",
        default="no",
    )

    test_multiple_time = Prompt.ask(
        "How many times do you want to run the test? ", default="1"
    )

    if isinstance(test_multiple_time, str) and test_multiple_time.isdigit():  # type: ignore
        test_multiple_time = int(test_multiple_time)
        if not isinstance(test_multiple_time, int) and test_multiple_time < 1:  # type: ignore
            print("Please input a number greater than 0.")
            continue

    if is_delete_db_test == "yes" or is_delete_db_test == "1":

        is_delete_db_test = True
        break

    elif is_delete_db_test == "no" or is_delete_db_test == "0":

        is_delete_db_test = False
        break

    else:
        print("Please input yes or no.")
        continue


base_url = f"http://localhost:{startport}"
testfile_folder = "testfile_folder"
os.makedirs(testfile_folder, exist_ok=True)

console = Console()


@handle_error
async def register_user(client: AsyncClient, user_t: dict[str, str]):
    print(f" 注册用户 {user_t}......")
    url = f"{base_url}/users/register"
    headers = {"Content-Type": "application/json"}
    data = user_t
    response = await client.post(url, headers=headers, json=data)

    responsejson = response.json()

    status_code = response.status_code

    if status_code == 200:
        assert responsejson["username"] == user_t["username"], "register failed"
    elif status_code == 400:
        assert responsejson["detail"] == "User already exists", "register failed"
    else:
        assert False, "unexpected register failed"


@handle_error
async def login_user(
    client: AsyncClient, user_t: dict[str, str], expected_status_code=200
):
    url = f"{base_url}/users/login"
    headers = {"Content-Type": "application/json"}
    data = user_t
    response = await client.post(url, headers=headers, json=data)

    assert response.status_code == expected_status_code, "error: login failed"
    if response.status_code == 200:
        token = response.json()["access_token"]
        refresh_token = response.json()["refresh_token"]
        return token

    print(f"用户登录: {user_t} , code: {response.status_code}", response.json())
    # print(response.json())


@handle_error
async def get_current_user(client, token, user_t, expected_status_code=200):
    print("获取当前用户信息......")
    url = f"{base_url}/users/me"
    headers = {"Authorization": f"Bearer {token}"}
    data = user_t
    response = await client.post(url, headers=headers, json=data)
    print(response.json())
    print(response.status_code)
    assert (
        response.status_code == expected_status_code
    ), "error: get current user failed"
    return response.json()


@handle_error
async def get_userid(client, token, user_t):
    print("获取当前用户id......")
    url = f"{base_url}/users/getid"
    headers = {"Authorization": f"Bearer {token}"}
    data = user_t
    response = await client.post(url, headers=headers, json=data)
    print(response.status_code)
    print(response.json())
    return response.json()


@handle_error
async def delete_user(client, token, user_t):
    print("删除用户......")
    user_info = await get_current_user(client, token, user_t)
    url = f"{base_url}/users/delete"
    headers = {"Authorization": f"Bearer {token}"}
    if user_info.get("id"):
        response = await client.delete(
            url, headers=headers, params={"id": user_info["id"]}
        )
        print(response.json())
    else:
        response = await client.delete(url, headers=headers)
        print(response.json())
    print(response.status_code)


@handle_error
async def upload_file(client: AsyncClient, token, test_file):
    print(f"上传文件 {test_file}......")
    url = f"{base_url}/files/upload"
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": open(test_file, "rb")}
    response = await client.post(url, headers=headers, files=files)
    print(response.status_code)
    print(response.json())
    return response.json()


@handle_error
async def download_file(client, token, test_file):
    print("下载文件......")
    file_json = await upload_file(client, token, test_file)
    file_id = file_json["id"]
    file_name = file_json["filename"]
    url = f"{base_url}/files/download"
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(url, headers=headers, params={"file_id": file_id})
    print(response.status_code)
    assert response.status_code == 200, "error: download file failed"
    with open(file_name, "wb") as f:
        f.write(response.content)


@handle_error
async def list_files(client, token):
    print("列出文件......")
    url = f"{base_url}/files/list"
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(url, headers=headers)
    print(response.status_code)
    print("文件列表原始数据：", response.json())
    files_id_name = [(d["id"], d["filename"]) for d in response.json()["files"]]
    return files_id_name


@handle_error
async def delete_file(client, token, file_id):
    print("删除文件......")
    url = f"{base_url}/files/delete"
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.delete(url, headers=headers, params={"file_id": file_id})
    print(response.status_code)
    print(response.json())


@handle_error
async def file_info(client, token, file_id):
    print("获取文件信息......")
    url = f"{base_url}/files/info"
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(url, headers=headers, params={"file_id": file_id})
    print(response.status_code)
    print(response.json())


@handle_error
async def delete_user_files(client, token):
    print("删除用户的所有文件......")
    url = f"{base_url}/users/files/delete"
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.delete(url, headers=headers)
    # print(response.status_code)
    response = await client.delete(url, headers=headers)
    response = await client.delete(url, headers=headers)
    response = await client.delete(url, headers=headers)
    print(response.status_code)
    # assert response.status_code == 200
    print(response.json())


@handle_error
async def reset_db(client, root, rootpassword):
    if is_delete_db_test:
        print("重置数据库......")
        url = f"{base_url}/db/reset"
        headers = {"Content-Type": "application/json"}
        data = {"username": root, "password": rootpassword}
        response = await client.post(url, headers=headers, json=data)
        print(response.status_code)
        assert response.status_code == 200, "error: reset_db failed"
        print(response.json())
    else:
        print("未删除数据库测试")


@handle_error
async def upload_file_with_nodes(client, token, test_file, nodes):
    data = {"file_nodes": nodes}
    print("上传文件以节点方式......", data)
    url = f"{base_url}/files/upload"
    headers = {"Authorization": f"Bearer {token}"}
    # print(headers)
    files = {"file": open(test_file, "rb")}
    print("file_nodes", json.dumps(nodes))
    response = await client.post(
        url, headers=headers, files=files, params={"file_nodes": json.dumps(nodes)}
    )
    print(response.status_code)
    print(response.json())

    if len(np.array(nodes).shape) == 1:

        assert response.json()["file_nodes"] == nodes or (
            response.json()["file_nodes"] == [] and nodes == [""]
        ), "error: upload_file_with_nodes failed"

    else:

        assert response.status_code != 200, "error: upload_file_with_nodes failed"

    return response


@handle_error
async def modyfy_file_nodes(client, token, file_id, nodes):

    url = f"{base_url}/file/modifynodes"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"file_nodes": json.dumps(nodes), "file_id": file_id}
    response = await client.post(url, headers=headers, params=params)
    print(response.status_code)
    print(response.json())
    if response.status_code == 200:
        print("修改文件节点", nodes, "resullt:", response.json()["file_nodes"])
        assert response.json()["file_nodes"] == nodes, "error: modify file nodes failed"


# @handle_error
async def Breakpoint_resume_download_test(client, token):

    # 测试文件生成
    test_upload_file = get_new_path(f"{testfile_folder}/testbinary.b")

    os.makedirs(testfile_folder, exist_ok=True)

    if os.path.exists(test_upload_file):

        os.remove(test_upload_file)

    def generate_random_binary_file(file_path, size_in_bytes):
        with open(file_path, "wb") as f:
            data = os.urandom(size_in_bytes)
            f.write(data)

    generate_random_binary_file(test_upload_file, 1024 * 1024 * 4)

    with open(test_upload_file, "rb") as f:

        original_bytes: bytes = f.read()

    original_bytes_size = os.path.getsize(test_upload_file)

    assert len(original_bytes) == original_bytes_size

    print(original_bytes_size)

    # 上传
    responsejson = await upload_file(client, token, test_upload_file)

    # 获取id
    file_id = responsejson["id"]

    print(file_id)

    # 下载
    headers = {"Authorization": f"Bearer {token}"}
    ranges = """
    Range: bytes=0-419430
    Range: bytes=419431-838860
    Range: bytes=838861-1258290
    Range: bytes=1258291-1677720
    Range: bytes=1677721-2097150
    Range: bytes=2097151-2516580
    Range: bytes=2516581-2936010
    Range: bytes=2936011-3355440
    Range: bytes=3355441-3774870
    Range: bytes=3774871-4194303
    """.strip()

    ranges_list = re.findall(r"bytes=(\d+-\d+)", ranges)

    async def download_part(client, headers, file_id, r: str = None) -> bytes:
        url = f"{base_url}/files/download/stream"
        params = {"file_id": file_id}
        if r:
            headers["Range"] = r
        response = await client.get(url, headers=headers, params=params)
        print(response.headers)
        return response.content

    # tasks = []

    get_byte_list = []

    len_get = 0

    for r in tqdm(ranges_list):
        # start, end = map(int, r.split("-"))
        # tasks.append(download_part(client, headers.copy(), file_id, start, end))
        print()
        print(r)
        start, end = map(int, r.split("-"))
        # print(start,end)
        b = await download_part(client, headers.copy(), file_id, r)
        print("len:", len(b))
        print(
            "start:",
            start,
            "end:",
            end,
            "len:",
            end - start + 1,
            "original:",
            original_bytes_size,
        )
        # assert len(b) == (end-start + 1)
        len_get += len(b)
        get_byte_list.append(b)

    # get_byte_list = await asyncio.gather(*tasks)
    all_get_bytes: bytes = bytearray(b"".join(get_byte_list))

    # ugizp = gzip.decompress(all_get_bytes)

    print("获取比特大小: ", len_get)
    print("原始比特大小: ", original_bytes_size)
    # print("解压后大小：",len(ugizp))

    assert len_get == original_bytes_size, "分片测试失败"

    print("分片测试通过")

    responseb = await download_part(client, headers.copy(), file_id=file_id)

    assert len(responseb) == original_bytes_size, "整体测试1失败"

    assert original_bytes == all_get_bytes, "整体测试2失败"

    # print(original_bytes_size)


# 刷新token
async def test_refreshtoken(client: AsyncClient, token: str) -> str:
    url = f"{base_url}/users/refresh"
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(url, headers=headers)
    print(response.status_code)
    print(response.json())
    return response.json()["access_token"]


# 修改文件名
async def test_modifyfilename(client: AsyncClient, token: str, file_id: str) -> dict:
    url = f"{base_url}/file/modifyname"
    headers = {"Authorization": f"Bearer {token}"}
    newfilename = f"{str(uuid4())}.txt"
    print("newfilename:", newfilename, "file_id:", file_id)
    response = await client.post(
        url, headers=headers, params={"file_id": file_id, "new_file_name": newfilename}
    )
    print(response.status_code)
    print(response.json())
    return response.json()


# 测试获取同属于一个节点路径的文件列表
async def test_getfilesbynode(client: AsyncClient, token: str, nodes: list):

    url = f"{base_url}/files/nodefiles"

    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(
        url, headers=headers, params={"file_nodes": json.dumps(nodes)}
    )

    print(response.status_code)

    print(response.json())


# 获取用户头像
async def test_getuseravatar(client: AsyncClient, token: str):
    url = f"{base_url}/users/profileimage"
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(url, headers=headers)

    print(response.status_code)
    assert response.status_code == 200

    if response.status_code == 200:
        # 从Content-Disposition头获取文件名
        content_disposition = response.headers.get("Content-Disposition")
        if content_disposition and "filename*=" in content_disposition:
            filename = (
                content_disposition.split("filename*=")[1].strip().strip("utf-8''")
            )
            filename = unquote(filename)
        elif content_disposition and "filename=" in content_disposition:
            filename = content_disposition.split("filename=")[1].strip().strip('"')
        else:
            filename = "userprofileimg.jpg"

        # 创建保存路径
        save_path = os.path.join("test", filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)  # 确保目录存在

        # 保存文件内容
        with open(save_path, "wb") as file:
            file.write(response.content)

        print(f"Profile image saved successfully as {save_path}.")
    else:
        print(f"Failed to retrieve profile image: {response.status_code}")
        print(response.json())


# 上传用户头像
async def test_uploaduseravatar(client: AsyncClient, token: str, test_file: str):

    url = f"{base_url}/users/upload/profileimage"

    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": open(test_file, "rb")}
    response = await client.post(url, headers=headers, files=files)

    print(
        f"test_file:{test_file}.  File size:",
        os.path.getsize(test_file) / (1024 * 1024),
        "MB",
    )

    print(response.status_code)
    if os.path.getsize(test_file) <= config.UserConfig.PROFILE_IMAGE_MAX_FILE_SIZE:
        assert response.status_code == 200
    else:
        # {'detail': 'profile image File size exceeds maximum limit'}
        print("File too large, expected 400 error", response.status_code)
        assert response.status_code == 400
        assert (
            response.json()["detail"] == "profile image File size exceeds maximum limit"
        )

    print(response.json())

    return response


# 获取图片预览
@handle_error
async def test_getimagepreview(client: AsyncClient, token: str):

    # 生成一个随机图片
    test_image = get_new_path(f"{testfile_folder}/testimage.jpg")
    if os.path.exists(test_image):
        os.remove(test_image)
    os.makedirs(os.path.dirname(test_image), exist_ok=True)
    image = generate_random_image(random.randint(100, 1000), random.randint(100, 1000))
    image.save(test_image)

    responsejson = await upload_file(client, token, test_image)

    file_id = responsejson["id"]

    url = f"{base_url}/files/img/preview"

    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(url, headers=headers, params={"file_id": file_id})

    print(response.status_code)

    assert response.status_code == 200, "error: get image preview failed"


# 测试视频预览
@handle_error
async def test_getvideopreview(client: AsyncClient, token: str):
    testvideo = get_new_path(f"{testfile_folder}/testvideo.mp4")
    if os.path.exists(testvideo):
        os.remove(testvideo)
    os.makedirs(os.path.dirname(testvideo), exist_ok=True)
    width, height = random.randint(100, 1000), random.randint(100, 1000)
    num_frames = random.randint(10, 100)
    fps = random.randint(10, 30)
    generate_random_video(width, height, num_frames, fps, testvideo)

    responsejson = await upload_file(client, token, testvideo)

    file_id = responsejson["id"]

    url = f"{base_url}/files/video/preview"

    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(url, headers=headers, params={"file_id": file_id})

    print(response.status_code)

    assert response.status_code == 200, "error: get video preview failed"


# 测试hls流
@handle_error
async def test_gethlsvideostram(client: AsyncClient, token: str):

    testvideo = get_new_path(f"{testfile_folder}/testhls.mp4")

    if os.path.exists(testvideo):
        os.remove(testvideo)

    os.makedirs(os.path.dirname(testvideo), exist_ok=True)

    width, height = random.randint(100, 400), random.randint(100, 400)

    fps = random.randint(10, 30)
    num_frames = random.randint(30, 60) * fps
    generate_random_video(width, height, num_frames, fps, testvideo)

    responsejson = await upload_file(client, token, testvideo)

    file_id = responsejson["id"]

    url = f"{base_url}/file/video/{file_id}/index.m3u8"

    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(url, headers=headers)

    print(response.status_code)

    assert response.status_code == 200, "error: get hls video stream failed"

    # print(response.text)

    index_m3u8 = response.text

    pattern = r".*\.ts$"

    segment_names = re.findall(pattern, index_m3u8, flags=re.MULTILINE)

    # print(segment_names)

    for seg in segment_names:

        url = f"{base_url}/file/segments/{file_id}/{seg}"

        response = await client.get(url, headers=headers)

        print(response.status_code)

        assert response.status_code == 200, f"error: get hls video segment {seg} failed"

        print(f"segment {seg} downloaded successfully")


async def main():
    async with httpx.AsyncClient(timeout=200) as client:
        user_t = dict(username=str(uuid4()), password=str(uuid4()))
        test_file = f"{testfile_folder}/{str(uuid4())}.txt"
        if not os.path.exists(test_file):
            os.makedirs(os.path.dirname(test_file), exist_ok=True)
            async with aiofiles.open(test_file, "w") as f:
                await f.write(f"{str(uuid4())}" * 10)
        await register_user(client, user_t)
        token = await login_user(client, user_t)
        # HTTP_401_UNAUTHORIZED
        for i in range(3):  #  登录错误测试
            usererror = await login_user(
                client, dict(username=str(uuid4()), password=str(uuid4())), 404
            )
            passworderror = await login_user(
                client, dict(username=user_t["username"], password=str(uuid4())), 401
            )

            await get_current_user(
                client, str(uuid4()), user_t, expected_status_code=401
            )
        if True:  ###初步测试 init_test
            await get_current_user(client, token, user_t)
            await delete_user(client, token, user_t)
            await register_user(client, user_t)
            token = await login_user(client, user_t)

            await get_current_user(client, token, user_t)
            await download_file(client, token, test_file)
            files_id_name = await list_files(client, token)
            print(files_id_name)
            for file_id, file_name in files_id_name:
                await file_info(client, token, file_id)
                await delete_file(client, token, file_id)
                print(f"Deleted file: {file_name}")
            files_id_names = await list_files(client, token)
            assert files_id_names == [], "error: delete files failed"
            await download_file(client, token, test_file)
            await delete_user_files(client, token)
            files_id_namess = await list_files(client, token)
            # expect no files because all files were deleted
            assert files_id_namess == [], "error: delete files failed"
            if os.path.exists(os.path.basename(test_file)):
                os.remove(os.path.basename(test_file))
        if True:  ###多文件测试
            for i in range(30):
                test_file = f"{testfile_folder}/{str(uuid4())}.txt"
                if not os.path.exists(test_file):
                    nodes = random.sample(
                        [["node1", "node2"], [], "node1", "node3", "node4", ""],
                        k=1,
                    )

                    os.makedirs(os.path.dirname(test_file), exist_ok=True)
                    async with aiofiles.open(test_file, "w") as f:
                        await f.write(f"{str(uuid4())}" * 10)
                print(f"test_file: {test_file}", "nodes:", nodes)
                await upload_file_with_nodes(client, token, test_file, nodes)
                if os.path.exists(os.path.basename(test_file)):
                    os.remove(os.path.basename(test_file))
            await delete_user_files(client, token)
        if True:  # 路径测试
            node1 = ["11", "22"]
            response = await upload_file_with_nodes(client, token, test_file, node1)
            # print()
            d_url = response.json()["file_download_link"]

            print(f"{base_url}{d_url}")

            file_id = response.json()["id"]
            nodess = [["11", "22", "33"], ["11"], [], ["11", "22"]]
            node2 = random.choice(nodess)
            await modyfy_file_nodes(client, token, file_id, node2)
        if True:  ###断点续传测试
            await Breakpoint_resume_download_test(client, token)

        if True:  ###其他测试 刷新token 修改文件名 获取文件列表
            token = await test_refreshtoken(client, token)
            await upload_file_with_nodes(
                client, token, test_file, ["11", "22", "testetst", "11111"]
            )
            await upload_file_with_nodes(
                client, token, test_file, ["testetst", "11111"]
            )
            await upload_file_with_nodes(client, token, test_file, ["11111"])
            await upload_file_with_nodes(client, token, test_file, [])
            fileid = (
                await upload_file_with_nodes(
                    client, token, test_file, ["11", "22", "testetst"]
                )
            ).json()["id"]
            print("fileid:", fileid)
            await test_modifyfilename(client, token, fileid)
            await test_getfilesbynode(client, token, ["11", "22", "testetst"])
            await test_getuseravatar(client, token)
            await test_uploaduseravatar(client, token, "test/image.png")
            await test_getuseravatar(client, token)
        if True:  # 上传大图像 头像测试
            bigimg = "./test/bigimg.jpg"
            re = await test_uploaduseravatar(client, token, bigimg)
            assert re.status_code == 400
        if True:  # 预览和hls测试
            await register_user(client, user_t)
            token = await login_user(client, user_t)
            await test_getimagepreview(client, token)
            await test_getvideopreview(client, token)
            await test_gethlsvideostram(client, token)
        # await delete_user(client, token, user_t)
        if is_delete_db_test:  #  删库测试 🤣
            async with httpx.AsyncClient(timeout=200) as client2:
                await reset_db(client2, root_user, root_password)


async def test_multiple(n):
    tasks = [asyncio.create_task(main()) for i in range(n)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":

    asyncio.run(test_multiple(test_multiple_time))

    def delete_test_folder(folder_to_delete):
        if os.path.exists(folder_to_delete):
            folder_to_delete = os.path.abspath(folder_to_delete)
        for i in range(5):
            if os.path.exists(folder_to_delete):
                shutil.rmtree(folder_to_delete, ignore_errors=True)
                for r, _, fs in os.walk(folder_to_delete):
                    for f in fs:
                        f_path = Path(r) / Path(f)
                        try:
                            os.remove(f_path)
                        except Exception as e:
                            pass
            if i != 0:
                pass

    delete_test_folder(testfile_folder)


# DROP TABLE whyshi.association CASCADE; DROP TABLE whyshi.users CASCADE;DROP TABLE whyshi.files CASCADE;
# DROP TABLE whyshi.association CASCADE; DROP TABLE whyshi.users CASCADE;
#  SELECT * FROM whyshi.files;SELECT * FROM whyshi.users;SELECT * FROM whyshi.association;
