from pydantic import BaseModel

class TableAndDescription(BaseModel):
    table_name: str
    description: str | None = None

class GenerateResponseRequest(BaseModel):
    request: str

class TableDecisionOutput(BaseModel):
    table_names: list[str]

class QueryGenerationOutput(BaseModel):
    result: str
   