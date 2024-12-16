from typing import Annotated
from pydantic import BaseModel
from fastapi import Header, HTTPException
from src.domain.models import *

async def get_token(token: Annotated[str, Header()]):
    if token != "sg_super_secret_token":
        raise HTTPException(status_code=400, detail="Token is invalid. Maybe it's something like sg_super_secret_token ?")


# Response examples for all the endpoints
response_examples = { 
    400: {"description": "Bad Request", "content": {
        "application/json": {"example": {"detail": "Please check the parameters"}}}},
    404: {"description": "Item not found", "content": {
        "application/json": {"example": {"detail": "Item not found"}}}},
}


items_db = {"project1": {"name": "zoe"}, 
            "project2": {"name": "calipso"}}

class ResponseMessage(BaseModel):
    detail: str = "Success"
    data: dict = items_db

# HTTP STATUS CODES
# 4xx Client Error
# 400 Bad Request
# 401 Unauthorized
# 403 Forbidden
# 404 Not Found
# 405 Method Not Allowed
# 406 Not Acceptable
# 407 Proxy Authentication Required
# 408 Request Timeout
# 409 Conflict

# 5xx Server Error
# 500 Internal Server Error
# 501 Not Implemented
# 502 Bad Gateway
# 503 Service Unavailable
