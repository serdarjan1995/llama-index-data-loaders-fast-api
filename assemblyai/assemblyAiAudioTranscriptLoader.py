from enum import Enum
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from llama_hub.assemblyai import AssemblyAIAudioTranscriptReader, TranscriptFormat

import assemblyai

app = FastAPI(title='AssemblyAI Audio Transcript Loader')

API_KEY_HEADER = APIKeyHeader(name='Token', auto_error=True)



class TranscriptRequest(BaseModel):
    file_path: str = Field(..., description='URL or local file path of the audio file to be transcribed.')
    transcript_format: TranscriptFormat = Field(default=TranscriptFormat.TEXT,
                                                description='Format of the transcription document.')

@app.post('/transcribe')
def transcribe(
        request: TranscriptRequest,
        config: Optional[dict] = None,
        token: str = Security(API_KEY_HEADER)
) -> List:
    if config is None:
        config = {}
    reader = AssemblyAIAudioTranscriptReader(
        file_path=request.file_path,
        config=assemblyai.TranscriptionConfig(**config),
        api_key=token,
    )
    try:
        docs = reader.load_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return list(docs)
