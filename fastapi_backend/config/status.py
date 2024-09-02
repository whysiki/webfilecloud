# encoding: utf-8

# from fastapi import status
from .base import Config


class StatusConfig(Config):
    HTTP_200_OK: int = 200
    HTTP_206_PARTIAL_CONTENT: int = 206
    HTTP_400_BAD_REQUEST: int = 400
    HTTP_401_UNAUTHORIZED: int = 401
    HTTP_403_FORBIDDEN: int = 403
    HTTP_404_NOT_FOUND: int = 404
    HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE: int = 416
    HTTP_500_INTERNAL_SERVER_ERROR: int = 500
