@REM scp -r dist root@8.138.124.53:/root/firecloud/fastapi_filecloud_backend/

@REM ssh root@8.138.124.53 'bash /root/firecloud/fastapi_filecloud_backend/nginx2.sh'


@REM # ps aux | grep gunicorn
@REM # nano config.py
@REM # sudo killall gunicorn
@REM # cd firecloud/fastapi_filecloud_backend && source myenv/bin/activate
@REM # gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b :8000 -D main:app

@REM # gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b :8000 main:app

@REM # uvicorn main:app --reload --host 0.0.0.0

@REM # reset_db("whysiki", "778899vvbbnnmmC")


@REM scp -r . root@8.138.124.53:/root/firecloud/fastapi_filecloud_backend/


@REM scp -r  root@8.138.124.53:/root/firecloud/fastapi_filecloud_backend/

scp -r main.py root@47.115.43.139:/root/fastapi_filecloud_backend/main.py
ssh root@47.115.43.139 "cd /root/fastapi_filecloud_backend && sudo killall gunicorn && gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b :8000 -D main:app"
