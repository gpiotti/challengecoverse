import boto3
from app.database import database, jobs
from app.models import Dataset


def get_boto3_session():
    session = boto3.session.Session(
        aws_access_key_id="admin",
        aws_secret_access_key="admin1234",
    )
    return session


async def create_pending_job(dataset: Dataset):
    query = jobs.insert().values(s3_path=dataset.s3_path)
    last_record_id = await database.execute(query)
    return last_record_id


async def update_job_status(job_id: int, status: str):
    query = (
        jobs.update(jobs)
        .where(jobs.columns.id == job_id)
        .values(status=status)
    )
    query_result = await database.execute(query)
    return query_result
