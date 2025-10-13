from pydantic import BaseModel, Field
from fastapi import UploadFile
from typing import Optional


class ResponseMessage(BaseModel):
    detail: str = "Success"
    data: Optional[list | dict] = None

class MultiFileUpload(BaseModel):
    file1: UploadFile = Field(..., description="Excel file")
    file2: UploadFile = Field(..., description="Json file")
