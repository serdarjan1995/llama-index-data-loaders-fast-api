from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional, Dict
from pydantic import BaseModel
from llama_hub.chroma import ChromaReader

app = FastAPI(title="Chroma DB loader")


class DocumentResponse(BaseModel):
    doc_id: str
    text: str
    embedding: List[float]


class RequestBody(BaseModel):
    query_vector: List[List[float]] = Query(..., description="Query vectors to load data")
    limit: int = Query(10, description="Number of results to return")
    where: Optional[Dict] = Query(None, description="Metadata where filter")
    where_document: Optional[Dict] = Query(None, description="Document where filter")
    persist_directory: str
    collection_name: str


@app.post('/load_data/', response_model=List[DocumentResponse])
def load_data(request_body: RequestBody):
    try:
        reader = ChromaReader(collection_name=request_body.collection_name,
                              persist_directory=request_body.persist_directory)
        return reader.load_data(query_vector=request_body.query_vector, limit=request_body.limit,
                                where=request_body.where, where_document=request_body.where_document)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
