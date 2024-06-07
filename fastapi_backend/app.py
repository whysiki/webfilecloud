# encoding: utf-8

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# origins = [
#     "http://localhost:3000",  # 允许本地开发服务器的跨域请求
#     "http://localhost:8080",  # 允许本地开发服务器的跨域请求
#     "http://localhost:8000",  # 允许本地开发服务器的跨域请求
#     "http://your-production-url.com",  # 允许生产服务器的跨域请求
# ]
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
