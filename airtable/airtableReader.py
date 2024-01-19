from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List
from llama_hub.airtable import AirtableReader
from llama_index import Document

app = FastAPI()

API_KEY_NAME = 'access_token'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if not api_key_header:
        raise HTTPException(status_code=403, detail='Could not validate credentials')
    return api_key_header


@app.get('/load-data', summary='Load data from Airtable',
          description='Load data from a specified table in a specified base from Airtable.',
          response_model=List[Document])
def load_data(base_id: str, table_id: str, api_key: str = Security(get_api_key)):
    reader = AirtableReader(api_key=api_key)
    try:
        data = reader.load_data(base_id=base_id, table_id=table_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))