from pydantic import BaseModel, Field

class TableAndDescription(BaseModel):
    table_name: str
    description: str | None = None
    columns: str | None = None

class GenerateResponseRequest(BaseModel):
    request: str

class TableDecisionOutput(BaseModel):
    table_names: list[str]

class QueryGenerationOutput(BaseModel):
    result: str

class DatabaseQueryResponse(BaseModel):
    rows: list
    columns: list[str]

class TableNameAndColumns(BaseModel):
    TableName: str
    Columns: list[str]

class TranslateModelOutput(BaseModel):
    TranslatedText: str = Field(description="The translated text in English")