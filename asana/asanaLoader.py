from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from typing import Optional, List
from pydantic import BaseModel
from llama_hub.asana import AsanaReader

app = FastAPI()

API_KEY_HEADER = APIKeyHeader(name='Asana-Token', auto_error=True)

class Document(BaseModel):
    text: str
    extra_info: dict

@app.get('/documents/', summary='Load documents from a workspace or project in Asana', response_model=List[Document])
async def get_documents(workspace_id: Optional[str] = None, project_id: Optional[str] = None, asana_token: str = Security(API_KEY_HEADER)):
    try:
        reader = AsanaReader(asana_token)
        return reader.load_data(workspace_id=workspace_id, project_id=project_id)
    except Exception as err:
        raise HTTPException(status_code=500, detail=repr(err))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
