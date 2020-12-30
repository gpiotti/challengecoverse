from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from app.settings import AppConfig
import databases
import sqlalchemy
from sqlalchemy.sql import func

config = AppConfig()


database = databases.Database(config.MYSQL_CONNECTION_STRING)


Base = declarative_base()

metadata = sqlalchemy.MetaData()

jobs = sqlalchemy.Table(
    "jobs",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True),
    sqlalchemy.Column("s3_path", sqlalchemy.String(200), unique=False),
    sqlalchemy.Column("start_time", sqlalchemy.DateTime, default=func.now()),
    sqlalchemy.Column("end_time", sqlalchemy.DateTime, default=None),
    sqlalchemy.Column("status", sqlalchemy.String(100), default="pending"),
)

engine = create_engine(config.MYSQL_CONNECTION_STRING)
metadata.create_all(engine)
