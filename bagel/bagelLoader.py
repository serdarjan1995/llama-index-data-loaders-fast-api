from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from llama_hub.bagel import BagelReader, Include

app = FastAPI()


class QueryModel(BaseModel):
    collection_name: str
    query_vector: Optional[list] = None
    query_text: Optional[str] = None
    include: Optional[Include] = ['metadatas', 'documents', 'embeddings', 'distances']
    limit: Optional[int] = 10
    where: Optional[str] = None
    where_document: Optional[str] = None


@app.post('/load_data/')
def load_data(
        query: QueryModel,
):
    try:
        reader = BagelReader(
            collection_name=query.collection_name
        )

        documents = reader.load_data(query_texts=query.query_text, query_vector=query.query_vector, limit=query.limit,
                                     include=query.include, where_document=query.where_document, where=query.where)

        return documents
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
