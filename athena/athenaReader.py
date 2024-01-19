from fastapi import FastAPI, HTTPException, Depends, Security
from llama_hub.athena import AthenaReader
from pydantic import BaseModel
from fastapi.security.api_key import APIKeyHeader
from llama_index.indices.struct_store import NLSQLTableQueryEngine
from llama_index import SQLDatabase, ServiceContext
from llama_index.llms import OpenAI

app = FastAPI(title='Athena Reader API')

aws_access_key_header_auth = APIKeyHeader(name='aws-access-key', auto_error=True, scheme_name='aws-access-key')
aws_access_secret_header_auth = APIKeyHeader(name='aws-access-secret', auto_error=True, scheme_name='aws-access-secret')
open_ai_api_key_header_auth = APIKeyHeader(name='openai-api-key', auto_error=True, scheme_name='openai-api-key')


class AccessKeys(BaseModel):
    aws_access_key: str
    aws_access_secret: str
    open_ai_api_key: str


async def get_api_key(aws_access_key: str = Depends(aws_access_key_header_auth),
                      aws_access_secret: str = Depends(aws_access_secret_header_auth),
                      open_ai_api_key: str = Depends(open_ai_api_key_header_auth)):
    if not aws_access_key or not aws_access_secret or not open_ai_api_key_header_auth:
        raise HTTPException(status_code=403, detail='Could not validate credentials')
    return AccessKeys(aws_access_key=aws_access_key, aws_access_secret=aws_access_secret,
                      open_ai_api_key=open_ai_api_key)


class AthenaEngineConfig(BaseModel):
    aws_region: str
    s3_staging_dir: str
    database: str
    workgroup: str
    table: str
    query: str


@app.post('/load-data', tags=['Athena Reader'])
async def create_athena_engine(config: AthenaEngineConfig, access_keys: AccessKeys = Depends(get_api_key)):
    try:
        llm = OpenAI(model="gpt-4", temperature=0, max_tokens=1024, api_key=access_keys.open_ai_api_key)

        engine = AthenaReader().create_athena_engine(
            aws_region=config.aws_region,
            s3_staging_dir=config.s3_staging_dir,
            database=config.database,
            workgroup=config.workgroup,
            aws_access_key=access_keys.aws_access_key,
            aws_secret_key=access_keys.aws_access_secret
        )

        service_context = ServiceContext.from_defaults(
            llm=llm
        )

        sql_database = SQLDatabase(engine, include_tables=[config.table])

        query_engine = NLSQLTableQueryEngine(
            sql_database=sql_database,
            tables=[config.table],
            service_context=service_context
        )

        response = query_engine.query(config.query)

        return response
    except Exception as err:
        raise HTTPException(status_code=500, detail=repr(err))
