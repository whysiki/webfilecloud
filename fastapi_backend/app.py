# encoding: utf-8

from fastapi import FastAPI
from config import Config
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

origins = Config.CORS_ORIGINS

minimum_size = Config.GZIP_MINIMUM_SIZE

# app = FastAPI(debug=True)
app = FastAPI()

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# noinspection PyTypeChecker
app.add_middleware(GZipMiddleware, minimum_size=minimum_size)
