from contextlib import asynccontextmanager
from fastapi import FastAPI

from nebula.database import Base, engine
from nebula.models import transcription
from nebula.routers.transcriptions import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(router)