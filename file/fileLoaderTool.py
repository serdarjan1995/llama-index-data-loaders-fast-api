from fastapi import FastAPI
from typing import List, Optional, Dict, Type
from llama_hub.file.pptx_slide import PptxSlideReader
from llama_index import SimpleDirectoryReader
from llama_index.readers.base import BaseReader
from llama_index.readers.file.base import DEFAULT_FILE_READER_CLS
from pydantic import BaseModel, Field

app = FastAPI(title="Simple Directory Reader")

class RequestBody(BaseModel):
    directory: str = Field(..., description='Path to the directory to load', alias='input_dir')
    exclude_hidden: Optional[bool] = Field(True, description='Whether to exclude hidden files')
    recursive: Optional[bool] = Field(False, description='Whether to search recursively in subdirectories')
    required_exts: Optional[List[str]] = Field(None, description='List of required file extensions')
    num_files_limit: Optional[int] = Field(1, description='Max number of files to read')


FILE_EXTRACTOR_MAPPING: Dict[str, BaseReader] = {
    ".pptx": PptxSlideReader(),
}


@app.post('/load-directory-data/', summary='Load documents from a directory')
async def load_directory_data(request_body: RequestBody):
    loader = SimpleDirectoryReader(
        input_dir=request_body.directory,
        exclude_hidden=request_body.exclude_hidden,
        recursive=request_body.recursive,
        required_exts=request_body.required_exts,
        num_files_limit=request_body.num_files_limit,
        file_extractor=FILE_EXTRACTOR_MAPPING,
    )
    documents = loader.load_data()
    return {'documents': documents}
