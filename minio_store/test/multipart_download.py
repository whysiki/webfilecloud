from fastapi import FastAPI, HTTPException, Request
import asyncio
from rich import print
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from minio import Minio
from minio.error import S3Error
import json
from fastapi.responses import StreamingResponse, Response
from fastapi import Depends

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1024)


def get_minio_client():
    with open("../credentials.json") as f:
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


# set alias
# ./mc alias set myminio http://localhost:9000  accesskey secretkey

# view all object in bucket
# ./mc ls --json --recursive myminio/testmulupload


# status: Indicates the status of the operation. In this case, it's "success", meaning the operation to retrieve information about the file was successful.

# type: Specifies the type of the object. Here, it's "file", indicating that the object referred to by this JSON is a file.

# lastModified: Shows the timestamp when the file was last modified. The format is ISO 8601 with timezone offset (YYYY-MM-DDTHH:MM:SS+HH:MM).

# size: Represents the size of the file in bytes. In this example, the file size is 1,211,437 bytes.

# key: This typically refers to the object key or name within the storage system. In this case, the key is "瑶湖cad.dwg".

# etag: ETag (Entity Tag) is a unique identifier assigned to the object. It helps in identifying changes to the object's content. This value is often used for cache validation in HTTP headers.

# url: Provides the URL where the file can be accessed or downloaded. In this example, the file is accessible at "http://localhost:9000/testmulupload/".

# versionOrdinal: Indicates the version ordinal of the object. Here, it's 1, meaning it's the first version of the object.

# storageClass: Specifies the storage class of the object. "STANDARD" typically refers to the standard storage class, which provides high durability and availability.
