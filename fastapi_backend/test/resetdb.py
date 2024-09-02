# encoding: utf-8

import requests
import json
from rich import print

# base_url = "http://8.138.124.53:8000"
base_url = "http://47.115.43.139:8000"


# 重置数据库
def reset_db(root, rootpassword):
    url = f"{base_url}/db/reset"
    data = {"username": root, "password": rootpassword}
    response = requests.post(url, data=json.dumps(data))
    print(response.json())
    # print("数据库已重置")
    # print(response.status_code)


# ps aux | grep gunicorn
# nano config.py
# sudo killall gunicorn
# cd firecloud/fastapi_filecloud_backend && source myenv/bin/activate
# gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b :8000 -D main:app

# gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b :8000 main:app

# uvicorn main:app --reload --host 0.0.0.0

# reset_db("whysiki", "778899vvbbnnmmC")
