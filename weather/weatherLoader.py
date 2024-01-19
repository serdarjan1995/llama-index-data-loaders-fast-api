from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from typing import List
from llama_hub.weather import WeatherReader
from pydantic import BaseModel

app = FastAPI()

API_KEY_NAME = 'access_token'
API_KEY_HEADER = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key_header: str = Security(API_KEY_HEADER)):
    if not api_key_header:
        raise HTTPException(status_code=403, detail='Could not validate credentials')
    return api_key_header

class PlaceList(BaseModel):
    places: List[str]

class WeatherDocument(BaseModel):
    text: str
    extra_info: dict

@app.post('/weather', response_model=List[WeatherDocument], summary='Get weather data for multiple locations', description='Fetches weather data from OpenWeatherMap API for a list of places. Requires an API key.')
def read_weather(places: PlaceList, api_key: APIKey = Depends(get_api_key)):
    loader = WeatherReader(token=api_key)
    try:
        results = loader.load_data(places=places.places)
    except Exception as err:
        raise HTTPException(status_code=403, detail=repr(err))
    return results
