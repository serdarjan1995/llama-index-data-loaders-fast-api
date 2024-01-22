from fastapi import FastAPI, HTTPException
from typing import Optional, List
from llama_hub.couchdb import SimpleCouchDBReader
from pydantic import BaseModel

app = FastAPI(title="CouchDb loader")


class Document(BaseModel):
    text: str


class RequestBody(BaseModel):
    host: str
    port: int = 5984
    user: str
    password: str
    db_name: str
    query_str: str
    max_docs: Optional[int] = 1000


@app.post('/load_data/', response_model=List[Document], summary='Load documents from CouchDB',
          description='Fetches documents from a specified CouchDB database based on the provided query.')
def read_couchdb_documents(request_body: RequestBody) -> List[Document]:
    reader = SimpleCouchDBReader(host=request_body.host, port=request_body.port, user=request_body.user,
                                 pwd=request_body.password, max_docs=request_body.max_docs)
    try:
        return reader.load_data(request_body.db_name, request_body.query_str)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
