from fastapi import FastAPI, HTTPException, Depends, Security, Query
from fastapi.security.api_key import APIKeyHeader, APIKey
from llama_hub.notion import NotionPageReader
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(title="Notion dataloader")

API_KEY_NAME = 'NOTION_INTEGRATION_SECRET'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


async def get_api_key(api_key_header: str = Security(api_key_header)):
    if not api_key_header:
        raise HTTPException(status_code=403, detail='Could not validate credentials')
    return api_key_header


class PageIds(BaseModel):
    page_ids: List[str] = Field(..., description='List of Notion page IDs to load')


class DatabaseId(BaseModel):
    database_id: str = Field(..., description='A single Notion database ID to query for page IDs')


@app.post('/load-pages/', summary='Load multiple pages from Notion')
def load_pages(page_ids: PageIds, api_key: str = Depends(get_api_key)):
    reader = NotionPageReader(integration_token=api_key)
    return reader.load_data(page_ids=page_ids.page_ids)


@app.post('/load-database/', summary='Load pages from a Notion database')
def load_database(database_id: DatabaseId, api_key: str = Depends(get_api_key)):
    reader = NotionPageReader(integration_token=api_key)
    return reader.load_data(database_id=database_id.database_id)


@app.get('/search/', summary='Search for pages in Notion matching the query')
def search_pages(
        query: str = Query(..., description='Query text to search within Notion'),
        api_key: str = Depends(get_api_key)
):
    reader = NotionPageReader(integration_token=api_key)
    return reader.search('query')
