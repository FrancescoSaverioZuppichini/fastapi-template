from fastapi import FastAPI, Request, Response
from routers import users
import time
import loguru
from loguru import logger
import sys
import orjson

app = FastAPI()

app.include_router(users.router, prefix="/users", tags=["users"])


def serialize(record):
    subset = {
        "timestamp": record["time"].timestamp(),
        "message": record["message"],
        "level": record["level"].name,
        "process": {"id": record["process"].id},
    }
    return orjson.dumps(subset).decode()


def patching(record):
    record["extra"]["serialized"] = serialize(record)


logger = logger.patch(patching)
logger.remove(0)
logger.add(sys.stderr, format="{extra[serialized]}")


logger.add(
    "app.log",
    rotation="50 MB",
    retention="2 week",
    # serialize=True,
    level="INFO",
    enqueue=True,
    format="{extra[serialized]}",
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = time.time() - start_time
    to_log = {
        "url": request.url.path,
        "request_body": request.body.__dict__,
        "status": response.status_code,
        "time": process_time,
    }
    logger.info(to_log)
    return response


@app.get("/")
async def root():
    return {"message": "Hello World"}
