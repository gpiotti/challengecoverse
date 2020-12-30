from fastapi import FastAPI
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import (
    async_streaming_bulk,
)
from app.models import Dataset
import awswrangler as wr
from app.helpers import (
    get_boto3_session,
    create_pending_job,
    update_job_status,
)
from app.settings import AppConfig
from http import HTTPStatus
from app.database import database

config = AppConfig()
es = AsyncElasticsearch(config.ELASTICSEARCH_HOSTS)
app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


async def download_dataset(dataset: Dataset):
    wr.config.s3_endpoint_url = config.S3_ENDPOINT_URL
    data_stream = wr.s3.read_csv(
        path=[dataset.s3_path],
        boto3_session=get_boto3_session(),
        sep="\t",
        encoding="utf-8",
        chunksize=100,
    )
    for chunk in data_stream:
        for row in chunk.fillna("").to_dict("records"):
            yield row


@app.get("/")
async def index():
    return await es.cluster.health()


@app.post("/index_new_dataset")
async def insert_new_dataset(dataset: Dataset):
    job_id = await create_pending_job(dataset)
    if not (await es.indices.exists(index=dataset.name)):
        await es.indices.create(index=dataset.name)

    async for _ in async_streaming_bulk(
        client=es,
        index=dataset.name,
        actions=download_dataset(dataset),
    ):
        pass
    job_id = await update_job_status(job_id, status="finished")

    return {
        "status": HTTPStatus.OK,
        **dataset.dict(),
    }


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
