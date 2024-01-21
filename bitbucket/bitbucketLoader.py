from fastapi import FastAPI, Security, HTTPException, Depends
from llama_hub.bitbucket import BitbucketReader
from pydantic import BaseModel
from typing import List, Optional
from fastapi.security.api_key import APIKeyHeader
import base64

app = FastAPI()

bitbucket_api_key_header_auth = APIKeyHeader(name='X-BITBUCKET-API-KEY', auto_error=True, scheme_name='bitbucket-api-key')
bitbucket_username_header_auth = APIKeyHeader(name='X-BITBUCKET-USERNAME', auto_error=True, scheme_name='bitbucket-username')

class AccessKeys(BaseModel):
    bitbucket_api_key: str
    bitbucket_username: str

async def get_api_key(bitbucket_api_key: str = Depends(bitbucket_api_key_header_auth),
                      bitbucket_username: str = Depends(bitbucket_username_header_auth)):
    if not bitbucket_api_key or not bitbucket_username:
        raise HTTPException(status_code=403, detail='Could not validate credentials')
    return AccessKeys(bitbucket_api_key=bitbucket_api_key, bitbucket_username=bitbucket_username)


class RequestBody(BaseModel):
    project_key: str
    base_url: str
    branch: str
    repository: str
    extensions_to_skip: Optional[List] = []


class BitbucketReaderAuth(BitbucketReader):
    def __init__(self, api_key: str, api_username: str, base_url: Optional[str] = None, project_key: Optional[str] = None,
                 branch: Optional[str] = "refs/heads/develop", repository: Optional[str] = None,
                 extensions_to_skip: Optional[List] = []) -> None:
        """Initialize with parameters."""
        if api_key is None:
            raise ValueError("Could not find a Bitbucket username.")
        if api_username is None:
            raise ValueError("Could not find a Bitbucket api key.")
        if base_url is None:
            raise ValueError("You must provide a base url for Bitbucket.")
        if project_key is None:
            raise ValueError("You must provide a project key for Bitbucket repository.")
        self.base_url = base_url
        self.project_key = project_key
        self.branch = branch
        self.extensions_to_skip = extensions_to_skip
        self.repository = repository
        self.api_key = api_key
        self.api_username = api_username


    def get_headers(self):
        auth = base64.b64encode(f"{self.api_username}:{self.api_key}".encode()).decode()
        return {"Authorization": f"Basic {auth}"}



@app.post('/load-data/', summary='Load data from Bitbucket repository.')
def load_data(request_body: RequestBody, access_keys: AccessKeys = Depends(get_api_key)):
    try:
        reader = BitbucketReaderAuth(
            base_url=request_body.base_url,
            project_key=request_body.project_key,
            branch=request_body.branch,
            repository=request_body.repository,
            extensions_to_skip=request_body.extensions_to_skip,
            api_key=access_keys.bitbucket_api_key,
            api_username=access_keys.bitbucket_username
        )
        documents = reader.load_data()
        return {'documents': [doc.dict() for doc in documents]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
