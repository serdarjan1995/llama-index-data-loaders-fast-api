from typing import List, Optional
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from llama_hub.chatgpt_plugin import ChatGPTRetrievalPluginReader
from llama_index import Document
from pydantic import BaseModel

app = FastAPI(title='ChatGpt plugin')

security = HTTPBearer()


def get_current_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials:
        return credentials.credentials
    else:
        raise HTTPException(status_code=403, detail='Not authenticated')


class RequestBody(BaseModel):
    query: str
    endpoint_url: str
    top_k: Optional[int] = 10
    separate_documents: Optional[bool] = True


@app.post('/query', response_model=List)
async def read_query(
        request_body: RequestBody,
        bearer_token: str = Depends(get_current_bearer_token)
):
    try:
        reader = ChatGPTRetrievalPluginReader(
            endpoint_url=request_body.endpoint_url,
            bearer_token=bearer_token
        )
        return reader.load_data(query=request_body.query, top_k=request_body.top_k,
                                separate_documents=request_body.separate_documents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
