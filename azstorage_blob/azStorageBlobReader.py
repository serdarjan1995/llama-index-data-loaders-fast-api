from typing import List, Optional, Union, Dict
from fastapi import FastAPI, HTTPException, Depends, Security
from pydantic import BaseModel
from llama_hub.azstorage_blob import AzStorageBlobReader

app = FastAPI(title='Azure Storage Blob Reader',
              description='Load files or iterate through directories from Azure Storage Blob.')


class ContainerReadRequest(BaseModel):
    container_name: str
    blob: Optional[str]
    name_starts_with: Optional[str]
    include: Optional[Union[str, List[str]]]
    connection_string: Optional[str]
    account_url: Optional[str]
    prefix: str = ''


@app.post('/read-container/', response_model=List[Dict])
def read_container(container_req: ContainerReadRequest):
    try:
        reader = AzStorageBlobReader(
            container_name=container_req.container_name,
            blob=container_req.blob,
            name_starts_with=container_req.name_starts_with,
            include=container_req.include,
            connection_string=container_req.connection_string,
            account_url=container_req.account_url,
            prefix=container_req.prefix
        )
        return reader.load_data()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
