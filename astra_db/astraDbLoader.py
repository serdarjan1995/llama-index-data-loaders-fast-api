from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List

from llama_hub.astra_db import AstraDBReader
from llama_index import Document
from pydantic import BaseModel

API_KEY_NAME = "access-token"

api_key_header_auth = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def get_api_key(
    api_key_header: str = Security(api_key_header_auth),
):
    if not api_key_header:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key_header


app = FastAPI()

class DataLoad(BaseModel):
    query_vector: List[float]
    limit: int = 10
    collection_name: str
    api_endpoint: str

@app.post("/load-data", summary="Load data from Astra DB", response_model=List[Document])
def load_data(
    data_load: DataLoad,

    api_key: str = Depends(get_api_key),
):
    try:
        reader = AstraDBReader(
            collection_name=data_load.collection_name,
            token=api_key,
            api_endpoint=data_load.api_endpoint,
            embedding_dimension=len(data_load.query_vector)
        )

        return reader.load_data(vector=data_load.query_vector, limit=data_load.limit)
    except Exception as err:
        raise HTTPException(status_code=500, detail=repr(err))
