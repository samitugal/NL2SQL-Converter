# server.py
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from main.Databases.Postgres import Postgres
from .config_defs import MainConfig
from sqlalchemy import create_engine

class GenerateResponseRequest(BaseModel):
    request: str

app = FastAPI()

config: MainConfig = MainConfig.from_file("/home/user/aiworkspace/configs/postgresql.yaml")
print("Using config from ", "/home/user/aiworkspace/configs/postgresql.yaml")

@app.post("/generate_response", status_code=status.HTTP_200_OK)
def generate_response(request: GenerateResponseRequest):
    try:
        database = Postgres(config)
        result = database.provide_table_names()
        print(result)
        database.disconnect()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/hello")
def hello():
    print(config)
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main.server:app", host="0.0.0.0", port=8000, reload=True)

