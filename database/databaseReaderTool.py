from typing import List, Optional
from fastapi import FastAPI, HTTPException
from llama_hub.database import DatabaseReader
from pydantic import BaseModel

app = FastAPI()


class Document(BaseModel):
    text: str


class DatabaseConfig(BaseModel):
    scheme: str = "postgres"
    host: str = "localhost"
    port: str = "5432"
    user: str = "postgres"
    password: str = "FakeExamplePassword"
    dbname: str = "postgres"


class RequestBody(BaseModel):
    query: str = """SELECT CONCAT(name, ' is ', age, ' years old.') AS text FROM public.users WHERE age >= 18"""
    connection_uri: Optional[str] = "{scheme}://{user}:{password}@{host}:{port}/{dbname}"
    db_config: Optional[DatabaseConfig] = None


@app.post('/load_data/', response_model=List[Document])
def load_data(request_body: RequestBody):
    try:
        if request_body.db_config:
            reader = DatabaseReader(scheme=request_body.db_config.scheme, host=request_body.db_config.host,
                                    port=request_body.db_config.port, dbname=request_body.db_config.dbname,
                                    user=request_body.db_config.user, password=request_body.db_config.password)
        elif request_body.uri:
            reader = DatabaseReader(uri=request_body.uri)
        else:
            raise HTTPException(status_code=400, detail='Insufficient database connection parameters')
        documents = reader.load_data(request_body.query)
        return documents
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
