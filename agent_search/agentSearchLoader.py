from typing import List

from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel

class Document(BaseModel):
    text: str
    metadata: dict

app = FastAPI()

API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if not api_key_header:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key_header

@app.get("/load_data", response_model=List[Document], summary="Load data from AgentSearch", description="This endpoint loads data using the AgentSearch API.", response_description="A list of documents as per the query.")
async def load_data(
    query: str = "",
    search_provider: str = "bing",
    llm_model: str = "SciPhi/Sensei-7B-V1",
    api_key: str = Security(get_api_key)
) -> List[Document]:
    try:
        from agent_search import SciPhi
    except ImportError:
        raise HTTPException(status_code=500, detail="'agent-search' package not found, please run 'pip install agent-search'")
    client = SciPhi(api_key=api_key)
    rag_response = client.get_search_rag_response(
        query=query, search_provider=search_provider, llm_model=llm_model
    )
    return [Document(text=rag_response.pop("response"), metadata=rag_response)]
