from pydantic import BaseModel


items_db = {"project1": {"name": "zoe"}, 
            "project2": {"name": "calipso"}}

class ResponseMessage(BaseModel):
    detail: str = "Success"
    data: dict = items_db
