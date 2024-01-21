from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from llama_hub.boarddocs import BoardDocsReader
from pydantic import BaseModel


app = FastAPI()


class Document(BaseModel):
    text: str
    doc_id: str
    extra_info: dict


@app.get('/meeting-list', summary='Retrieve meeting list', response_model=List[dict])
async def get_meeting_list(site: str, committee_id: str):
    try:
        board_docs_reader_instance = BoardDocsReader(site=site, committee_id=committee_id)
        return board_docs_reader_instance.get_meeting_list()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get('/process-meeting/{meeting_id}', summary='Retrieve documents from a meeting')
async def process_meeting(meeting_id: str, site: str, committee_id: str):
    try:
        board_docs_reader_instance = BoardDocsReader(site=site, committee_id=committee_id)
        return board_docs_reader_instance.process_meeting(meeting_id=meeting_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get('/load-data', summary='Load all meetings and documents')
async def load_data(site: str, committee_id: str, meeting_ids: List[str] = Query(None)):
    try:
        loader = BoardDocsReader(site=site, committee_id=committee_id)
        documents = loader.load_data(meeting_ids=meeting_ids)
        return documents
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
