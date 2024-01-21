from typing import List
from fastapi import FastAPI, HTTPException
from llama_hub.bilibili import BilibiliTranscriptReader
from pydantic import BaseModel


app = FastAPI(title='Bilibili Transcript Loader')


class VideoURL(BaseModel):
    urls: List[str]


@app.post('/transcripts/', summary='Load Bilibili video transcripts',
          description='Fetches transcripts for an array of Bilibili video URLs. Returns a list of transcripts.')
async def load_transcripts(video_url: VideoURL):
    loader = BilibiliTranscriptReader()
    try:
        documents = loader.load_data(video_urls=video_url.urls)
        return {'documents': [doc.text for doc in documents]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
