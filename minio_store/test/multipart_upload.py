from fastapi import FastAPI, File, UploadFile, HTTPException, Request
import os
import aiofiles
import shutil
from rich import print
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pathlib import Path
from minio import Minio
from minio.error import S3Error
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1024)


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


# MinIO 存储桶名称
bucket_name = "testmulupload"
found = client.bucket_exists(bucket_name)
if not found:
    client.make_bucket(bucket_name)

# 临时文件夹
TEMP_UPLOAD_DIR = "temp_upload_dir"


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
async def merge_files(filename: str, file_id: str):

    print(filename, file_id)
    temp_upload_dir = os.path.join(TEMP_UPLOAD_DIR, file_id)
    # 找到所有分片文件
    parts = os.listdir(temp_upload_dir)
    parts.sort()  # 确保按顺序合并

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


# Request Syntax
# response = client.create_multipart_upload(
#     ACL='private'|'public-read'|'public-read-write'|'authenticated-read'|'aws-exec-read'|'bucket-owner-read'|'bucket-owner-full-control',
#     Bucket='string',
#     CacheControl='string',
#     ContentDisposition='string',
#     ContentEncoding='string',
#     ContentLanguage='string',
#     ContentType='string',
#     Expires=datetime(2015, 1, 1),
#     GrantFullControl='string',
#     GrantRead='string',
#     GrantReadACP='string',
#     GrantWriteACP='string',
#     Key='string',
#     Metadata={
#         'string': 'string'
#     },
#     ServerSideEncryption='AES256'|'aws:kms'|'aws:kms:dsse',
#     StorageClass='STANDARD'|'REDUCED_REDUNDANCY'|'STANDARD_IA'|'ONEZONE_IA'|'INTELLIGENT_TIERING'|'GLACIER'|'DEEP_ARCHIVE'|'OUTPOSTS'|'GLACIER_IR'|'SNOW'|'EXPRESS_ONEZONE',
#     WebsiteRedirectLocation='string',
#     SSECustomerAlgorithm='string',
#     SSECustomerKey='string',
#     SSEKMSKeyId='string',
#     SSEKMSEncryptionContext='string',
#     BucketKeyEnabled=True|False,
#     RequestPayer='requester',
#     Tagging='string',
#     ObjectLockMode='GOVERNANCE'|'COMPLIANCE',
#     ObjectLockRetainUntilDate=datetime(2015, 1, 1),
#     ObjectLockLegalHoldStatus='ON'|'OFF',
#     ExpectedBucketOwner='string',
#     ChecksumAlgorithm='CRC32'|'CRC32C'|'SHA1'|'SHA256'
# )

# Response Syntax
# {
#     "AbortDate": datetime(2015, 1, 1),
#     "AbortRuleId": "string",
#     "Bucket": "string",
#     "Key": "string",
#     "UploadId": "string",
#     "ServerSideEncryption": "AES256" | "aws:kms" | "aws:kms:dsse",
#     "SSECustomerAlgorithm": "string",
#     "SSECustomerKeyMD5": "string",
#     "SSEKMSKeyId": "string",
#     "SSEKMSEncryptionContext": "string",
#     "BucketKeyEnabled": True | False,
#     "RequestCharged": "requester",
#     "ChecksumAlgorithm": "CRC32" | "CRC32C" | "SHA1" | "SHA256",
# }


# minio.error.S3Error:
# S3 operation failed; code: EntityTooSmall,
# message: Your proposed upload is smaller than the minimum allowed object size.

# Special errors
# Error Code: EntityTooSmall

# Description: Your proposed upload is smaller than the minimum allowed object size. Each part must be at least 5 MB in size, except the last part.

# HTTP Status Code: 400 Bad Request

# Error Code: InvalidPart

# Description: One or more of the specified parts could not be found. The part might not have been uploaded, or the specified ETag might not have matched the uploaded part's ETag.

# HTTP Status Code: 400 Bad Request

# Error Code: InvalidPartOrder

# Description: The list of parts was not in ascending order. The parts list must be specified in order by part number.

# HTTP Status Code: 400 Bad Request

# Error Code: NoSuchUpload

# Description: The specified multipart upload does not exist. The upload ID might be invalid, or the multipart upload might have been aborted or completed.

# HTTP Status Code: 404 Not Found
