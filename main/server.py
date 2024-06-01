# server.py
import pandas as pd
import numpy as np

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
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str

    class Config:
        env_file = ".env"

app = FastAPI()
envvars = MainRuntimeVars()

database_config: MainConfig = MainConfig.from_file(envvars.DATABASE_CONNECTION_PATH)
print(f"Using config from {envvars.DATABASE_CONNECTION_PATH}")
llm_config: LLMMainConfig = LLMMainConfig.from_file(envvars.LLM_CONFIG_PATH)
print(f"Using config from {envvars.LLM_CONFIG_PATH}")

@app.post("/generate_response", status_code=status.HTTP_200_OK)
def generate_response(request: GenerateResponseRequest):
    # try:
        database = Database.new_instance_from_config(config=database_config)
        table_names_and_descriptions = database.provide_table_names()
        database.disconnect()

        llm = Pipeline.new_instance_from_config(config=llm_config)
        table_names_result = llm.return_table_names_list(request=request, table_names_and_descriptions=table_names_and_descriptions)

        table_names_and_columns = database.provide_column_names_of_tables(table_names=table_names_result.table_names)
        query_result = llm.generate_sql_query_step(request=request, table_names=table_names_result, 
                                                                    column_list= table_names_and_columns, sql_type=database_config.db.database_tag)
        try:
            result = database.execute_query(query=query_result.result)
            columns = result.columns
            rows = result.rows
            data = [dict(zip(columns, row)) for row in rows]

            # Creating DataFrame from the list of dictionaries
            df = pd.DataFrame(data)

            # Convertion Numpy to Json Convertible Version
            json_compatible_data = df.replace({np.nan: None}).applymap(
                lambda x: x.item() if isinstance(x, (np.integer, np.floating, np.bool_)) else x
            ).to_dict(orient='records')

            final_result = {
                "database": database_config.db.database_tag,
                "query": query_result.result,
                "result": json_compatible_data
            }

            return final_result

        finally:
            database.disconnect()

    # except Exception as e:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/hello")
def hello():
    print(config)
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main.server:app", host="0.0.0.0", port=8000, reload=True)

