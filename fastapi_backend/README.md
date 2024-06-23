
## 自用简单云盘服务器后端模板

## 使用说明

- 数据库使用PostgreSQL
- `app.py`为ASGI应用实例，里面可以配置中间件、路由等
- `main.py`为API路由定义
- `models.py`为数据库模型定义
- `schemas.py`为Pydantic模型定义
- `crud.py`为数据库操作函数
- `config.py`为配置文件
- `utility.py`为工具函数
- `dep.py`为依赖注入
- `auth.py`为认证函数
- `test_files1.py`为测试文件
- `env.py` 生成`.env`文件
- `start.py`自用部署脚本

- 修改`.env`文件中的数据库连接信息为自己的数据库连接信息, 需要赋予数据库用户数据库的权限和public schema的权限


由于未做分页处理，所以不能处理过多数据，具体看服务器配置。🥲


### 依赖安装

基础依赖

`pip install -r requirements.txt`

数据库驱动

- `pip install psycopg2` in windows
- `sudo apt install python3-psycopg2`, `sudo apt install libpq-dev` in ubuntu


### 调试启动

示例：
`python3 -m uvicorn main:app --reload`
or
`python3 -m hypercorn main:app --reload`

### 部署

示例：监听8000端口，使用4个进程，使用uvicorn工作进程，后台运行，监听所有地址

`gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b :8000 -D main:app`

实际部署时，配置域名、SSL证书、反向代理等

### api document 

view in `http://127.0.0.1:8000/redoc` or `http://127.0.0.1:8000/docs`

or

view in `http://yourapiserveraddress/redoc` or `http://yourapiserveraddress/docs`