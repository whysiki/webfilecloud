
## 自用简单云盘服务器后端模板

## 使用说明

数据库使用PostgreSQL 对象存储采用 minio ,支持存储在本地或者minio服务器

- `app.py`为ASGI应用实例，里面可以配置中间件、路由等
- `main.py`为API路由定义
- `models.py`为数据库模型定义
- `schemas.py`为Pydantic模型定义
- `crud.py`为数据库操作函数
- `config.py`为配置文件
- `utility.py`为工具函数
- `dep.py`为依赖注入
- `auth.py`为认证函数
- `test_files.py`为测试文件 可以看一些接口调用的示例
- `env.py` 生成`.env`文件
- `start.py`自用部署脚本
- `storage_.py` 为封装的文件存储函数
- `test_multipart_download.html` 为测试分片多线程下载的html文件仅仅对于minio服务器有效
- `test_multipart_upload.html` 为测试分片多线程上传的html文件仅仅对于minio服务器有效


修改`.env`文件中的数据库连接信息为自己的数据库连接信息, 需要赋予数据库用户数据库的权限和public schema的权限

```shell
# .env

# 上传文件存储路径
UPLOAD_PATH=uploads 
# 用于生成token的密钥
SECRET_KEY=b1f974fc-c181-4d1e-99ce-37d3c7c43551 
# token加密算法
ALGORITHM=HS256
# token过期时间
ACCESS_TOKEN_EXPIRE_MINUTES=30
# 管理员用户名 现在没用 只写了一个删库的接口🥲
ROOT_USER=whysiki
# 管理员密码
ROOT_PASSWORD=180cfgadd88-e429-40db-f9edfg49-c080cd629af1 
# 数据库连接信息 数据库必须要支持Column, String, Table, ForeignKey, ARRAY 类型
# DATABASE_URL=postgresql://username:password@localhost:port/database
DATABASE_URL=postgresql://postgres:whysiki@localhost:61111/filecloud
# 启动端口 测试时使用 实际服务启动端口还是看gunicorn或者uvicorn的启动端口
START_PORT=8000
# 存储类型 minio / local , local为本地存储, minio为minio服务器存储
STORE_TYPE=minio
# minio服务器地址 不需要http://
MINIO_ENDPOINT=localhost:9000
# minio服务器访问密钥
MINIO_ACCESS_KEY=minioadmin
# minio服务器
MINIO_SECRET_KEY=minioadmin
# minio服务器是否启用https
MINIO_SECURE=False
# minio服务器存储桶
MINIO_BUCKET=filecloud
```

由于未做分页处理，所以不能处理过多数据，具体看服务器配置。


### 依赖安装

- 基础依赖

`pip install -r requirements.txt`

- 数据库安装和配置 
  - 下载 配置环境变量 略
  - 登录 `psql -U postgres -p 61111`  -p 61111 是端口号 -U postgres  用户名
  - 创建数据库 `CREATE DATABASE filecloud;`

- 数据库驱动

- `pip install psycopg2` in windows
- `sudo apt install python3-psycopg2`, `sudo apt install libpq-dev` in ubuntu


### 调试启动

示例：
`python3 -m uvicorn main:app --reload`
or
`python3 -m hypercorn main:app --reload`

默认启动端口为8000。

### 部署

示例：监听8000端口，使用4个进程，使用uvicorn工作进程，后台运行，监听所有地址

`gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b :8000 -D main:app`

实际部署时，配置域名、SSL证书、反向代理等

### api document 

view in `http://127.0.0.1:8000/redoc` or `http://127.0.0.1:8000/docs`

or

view in `http://yourapiserveraddress/redoc` or `http://yourapiserveraddress/docs`