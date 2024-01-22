from fastapi import FastAPI, HTTPException
from llama_hub.dad_jokes import DadJokesReader
from pydantic import BaseModel

class Document(BaseModel):
    text: str

app = FastAPI(title="DadJokes loader")

@app.get('/random-joke', summary='Get a Random Dad Joke', response_model=Document, tags=['Dad Jokes'])
async def get_random_dad_joke():
    """Fetch a random dad joke from icanhazdadjoke."""
    try:
        loader = DadJokesReader()
        documents = loader.load_data()
        return Document(text=documents[0].text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
