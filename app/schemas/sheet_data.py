from pydantic import BaseModel
from typing import List


class SheetData(BaseModel):
    data: List[List[str]]
