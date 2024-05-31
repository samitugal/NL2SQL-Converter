# server.py
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine

from .database_config_defs import MainConfig
from .llm_config_defs import LLMMainConfig
from .models import GenerateResponseRequest
from .Databases.Database import Database
from .LLM.Pipeline import Pipeline
from main.Databases.Postgres import Postgres

class MainRuntimeVars(BaseSettings):
    DATABASE_CONNECTION_PATH: str
    LLM_CONFIG_PATH: str

    class Config:
        env_file = ".env"

app = FastAPI()
envvars = MainRuntimeVars()

database_config: MainConfig = MainConfig.from_file(envvars.DATABASE_CONNECTION_PATH)
print(f"Using config from {envvars.DATABASE_CONNECTION_PATH}")
llm_config: LLMMainConfig = LLMMainConfig.from_file(envvars.LLM_CONFIG_PATH)
print("Using config from {envvars.LLM_CONFIG_PATH}}")

@app.post("/generate_response", status_code=status.HTTP_200_OK)
def generate_response(request: GenerateResponseRequest):
    # try:
    database = Database.new_instance_from_config(config= database_config)
    table_names_and_descriptions = database.provide_table_names()
    database.disconnect()
    ##
    llm = Pipeline.new_instance_from_config(config=llm_config)
    result = llm.return_table_names_list(request= request, table_names_and_descriptions= table_names_and_descriptions)
    return result
    # except Exception as e:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/hello")
def hello():
    print(config)
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main.server:app", host="0.0.0.0", port=8000, reload=True)

