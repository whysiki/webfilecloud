from fastapi import FastAPI, HTTPException, Request, File, UploadFile
import aiofiles
import asyncio
from rich import print
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from minio import Minio
from minio.error import S3Error
import json
from fastapi.responses import StreamingResponse, Response
from fastapi import Depends
import os
import shutil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1024)


# 临时文件夹
TEMP_UPLOAD_DIR = "temp_upload_dir"


def get_minio_client():
    with open("./credentials.json") as f:
        cre = json.load(f)
        print(cre)

    access_key = cre["accessKey"]
    secret_key = cre["secretKey"]

    client = Minio(
        endpoint="localhost:9000",
        access_key=access_key,
        secret_key=secret_key,
        secure=False,  # use http
    )
    return client


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
        range_header = f"bytes={current_position}-{current_position + read_size - 1}"

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


def get_file_size(
    client: Minio, bucket_name: str, object_name: str, *args, **kwargs
) -> int:
    try:
        stat = client.stat_object(bucket_name, object_name)
        return stat.size
    except S3Error as err:
        print(f"Error getting size for {object_name}: {err}")
        return 0


@app.get("/file/download/{bucket_name}/{object_name}")
@app.head("/file/download/{bucket_name}/{object_name}")
async def download_file(
    request: Request,
    object_name: str,
    bucket_name: str,
    client: Minio = Depends(get_minio_client),
):

    file_size = get_file_size(
        client=client, bucket_name=bucket_name, object_name=object_name
    )

    if not file_size:

        raise HTTPException(status_code=404, detail="No file data.")

    if request.method == "HEAD":
        headers = {
            "Content-Length": str(file_size),
            "Accept-Ranges": "bytes",
        }
        return Response(headers=headers)

    range_header = request.headers.get("Range")

    if range_header:
        try:
            start, end = range_header.replace("bytes=", "").split("-")
            start = int(start)
            end = int(end) if end else file_size - 1
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Range header")
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid Range header:{str(e)}"
            )
    else:
        start = 0
        end = file_size - 1

    if start >= file_size or end >= file_size:
        raise HTTPException(status_code=416, detail="Requested Range Not Satisfiable")

    return StreamingResponse(
        minio_file_iterator(
            client=client,
            bucket_name=bucket_name,
            object_name=object_name,
            start=start,
            end=end,
        ),
        status_code=206 if range_header else 200,
        headers={
            "Content-Length": str(end - start + 1),
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
        },
    )


# file_id is not object_name
@app.post("/upload/")
async def upload_file(file_id: str, order: str, upload_file: UploadFile = File(...)):
    try:
        print(file_id, order)
        # 创建临时文件目录
        temp_upload_dir = os.path.join(TEMP_UPLOAD_DIR, file_id)
        os.makedirs(temp_upload_dir, exist_ok=True)

        temp_file_path = os.path.join(temp_upload_dir, order)

        # 写入文件
        async with aiofiles.open(temp_file_path, "wb") as f:
            await f.write(await upload_file.read())

        # 返回临时文件目录和文件名以备后续合并
        return {"temp_upload_dir": temp_upload_dir, "filename": order, "code": 200}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error occurred during upload: {type(e)}, {str(e)}"
        )


@app.post("/merge/")
async def merge_files(
    bucket_name: str,
    filename: str,  # is object_name
    file_id: str,
    client: Minio = Depends(get_minio_client),
):

    print(filename, file_id)
    temp_upload_dir = os.path.join(TEMP_UPLOAD_DIR, file_id)
    # 找到所有分片文件
    parts = sorted(os.listdir(temp_upload_dir))

    print(parts)

    headers = {"Content-Type": "application/octet-stream"}

    # 创建 MinIO 的分片上传会话
    upload_id = client._create_multipart_upload(
        bucket_name=bucket_name,
        object_name=filename,
        headers=headers,
    )

    print(upload_id)

    # 逐个上传分片
    for i, part in enumerate(parts):
        part_path = os.path.join(temp_upload_dir, part)
        part_number = i + 1
        async with aiofiles.open(part_path, "rb") as data:
            data = await data.read()
            etag = client._upload_part(
                bucket_name=bucket_name,
                object_name=filename,
                part_number=part_number,  # 分片编号从 1 开始
                upload_id=upload_id,
                data=data,
                headers=None,
            )
            print(part_path, len(data))
            print(etag)

    list_parts = client._list_parts(
        bucket_name=bucket_name,
        object_name=filename,
        upload_id=upload_id,
    ).parts

    print(list_parts)

    for p in list_parts:

        print(p.size, p.part_number)

    # 完成分片上传
    client._complete_multipart_upload(
        bucket_name=bucket_name,
        object_name=filename,
        upload_id=upload_id,
        parts=list_parts,
    )

    # 删除临时分片文件目录
    shutil.rmtree(temp_upload_dir, ignore_errors=True)

    return {"message": "File uploaded successfully", "code": 200}
