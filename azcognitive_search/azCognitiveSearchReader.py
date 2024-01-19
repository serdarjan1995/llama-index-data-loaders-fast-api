from fastapi import FastAPI, Depends, HTTPException, Query, Security
from typing import List, Optional

from fastapi.security import APIKeyHeader
from llama_hub.azcognitive_search import AzCognitiveSearchReader
from pydantic import BaseModel

app = FastAPI(title='Azure Cognitive Search Loader')

api_key_header = APIKeyHeader(name='Search-Key', auto_error=True)


class Document(BaseModel):
    text: str
    extra_info: dict


class SearchQuery(BaseModel):
    query: str
    content_field: str
    filter: Optional[str] = None
    service_name: str
    index: str


async def get_search_key(search_key: str = Security(api_key_header)):
    if not search_key:
        raise HTTPException(status_code=403, detail='Could not validate credentials')
    return search_key


@app.post('/search', response_model=List[Document])
async def search_documents(
        search_query: SearchQuery,
        search_key: str = Security(get_search_key)
):
    reader = AzCognitiveSearchReader(
        service_name=search_query.service_name,
        index=search_query.index,
        searck_key=search_key,
    )

    documents = reader.load_data(
        query=search_query.query, content_field=search_query.content_field, filter=search_query.filter
    )

    return documents
