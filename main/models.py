from pydantic import BaseModel

class TableAndDescription(BaseModel):
    table_name: str
    description: str | None = None

class GenerateResponseRequest(BaseModel):
    request: str