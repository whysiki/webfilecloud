# encoding: utf-8

from fastapi import FastAPI
from config import Config
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

origins = Config.CROS_ORIGINS

minimum_size = Config.GZIP_MINIMUM_SIZE

# origins = [
#     "http://localhost:3000",  # 允许本地开发服务器的跨域请求
#     "http://localhost:8080",  # 允许本地开发服务器的跨域请求
#     "http://localhost:8000",  # 允许本地开发服务器的跨域请求
#     "http://your-production-url.com",  # 允许生产服务器的跨域请求
# ]


app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=minimum_size)


# Add prometheus asgi middleware to route /metrics requests
# metrics_app = make_asgi_app()
# app.mount("/metrics", metrics_app)
