from pydantic import BaseModel
import datetime


class Dataset(BaseModel):
    name: str
    description: str
    s3_path: str


class Job(BaseModel):
    id: int
    s3_path: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    status: str
