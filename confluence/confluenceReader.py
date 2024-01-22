from fastapi import FastAPI, HTTPException, Query, Depends, Security
from fastapi.security import OAuth2AuthorizationCodeBearer, APIKeyHeader
from typing import Optional, List
from pydantic import BaseModel
from llama_hub.confluence import ConfluenceReader
import logging

logging.getLogger().setLevel(logging.INFO)

app = FastAPI(title="Confluence loader")

oauth2_scheme = OAuth2AuthorizationCodeBearer(authorizationUrl='https://auth.atlassian.com',
                                              tokenUrl='https://auth.atlassian.com/oauth/token')


class TokenScheme(BaseModel):
    access_token: str
    token_type: str = "bearer"


class OauthScheme(BaseModel):
    client_id: str
    token: TokenScheme


class Document(BaseModel):
    text: str
    doc_id: str
    extra_info: dict


class RequestBodyWithSpaceKey(BaseModel):
    base_url: str = 'https://yoursite.atlassian.com/wiki'
    space_key: str = None
    page_status: Optional[str] = None
    include_attachments: bool = True
    start: Optional[int] = None
    max_num_results: Optional[int] = None
    oauth2: OauthScheme = Depends(oauth2_scheme)


class RequestBodyWithPageIds(BaseModel):
    base_url: str = 'https://yoursite.atlassian.com/wiki'
    page_ids: Optional[List[str]] = None
    include_attachments: bool = True
    include_children: bool = False
    start: Optional[int] = None
    max_num_results: Optional[int] = None
    oauth2: OauthScheme = Depends(oauth2_scheme)


class RequestBodyWithLabel(BaseModel):
    base_url: str = 'https://yoursite.atlassian.com/wiki'
    label: Optional[str] = None
    include_attachments: bool = True
    start: Optional[int] = None
    max_num_results: Optional[int] = None
    oauth2: OauthScheme = Depends(oauth2_scheme)


class RequestBodyWithCQL(BaseModel):
    base_url: str = 'https://yoursite.atlassian.com/wiki'
    cql: Optional[str] = None
    start: Optional[int] = None
    max_num_results: Optional[int] = None
    oauth2: OauthScheme = Depends(oauth2_scheme)


@app.post('/load-data-page-ids', response_model=List[Document], summary='Load data from Confluence filter by pageIds')
def load_data(request_body: RequestBodyWithPageIds):
    reader = ConfluenceReader(base_url=request_body.base_url, oauth2=request_body.oauth2.model_dump(), cloud=True)
    documents = reader.load_data(
        page_ids=request_body.page_ids,
        include_attachments=request_body.include_attachments,
        include_children=request_body.include_children,
        start=request_body.start,
        max_num_results=request_body.max_num_results
    )
    print(documents)
    return documents


@app.post('/load-data-space-key', response_model=List[Document],
          summary='Load data from Confluence filter by space key')
def load_data(request_body: RequestBodyWithSpaceKey):
    reader = ConfluenceReader(base_url=request_body.base_url, oauth2=request_body.oauth2.model_dump(), cloud=True)
    documents = reader.load_data(
        space_key=request_body.space_key,
        page_status=request_body.page_status,
        include_attachments=request_body.include_attachments,
        start=request_body.start,
        max_num_results=request_body.max_num_results
    )
    return documents


@app.post('/load-data-label', response_model=List[Document], summary='Load data from Confluence filter by label')
def load_data(request_body: RequestBodyWithLabel):
    reader = ConfluenceReader(base_url=request_body.base_url, oauth2=request_body.oauth2.model_dump(), cloud=True)
    documents = reader.load_data(
        label=request_body.label,
        include_attachments=request_body.include_attachments,
        start=request_body.start,
        max_num_results=request_body.max_num_results
    )
    return documents


@app.post('/load-data-cql', response_model=List[Document], summary='Load data from Confluence filter by CQL')
def load_data(request_body: RequestBodyWithCQL):
    reader = ConfluenceReader(base_url=request_body.base_url, oauth2=request_body.oauth2.model_dump(), cloud=True)
    documents = reader.load_data(
        cql=request_body.cql,
        start=request_body.start,
        max_num_results=request_body.max_num_results
    )
    return documents
