from fastapi import FastAPI, HTTPException
from src.api import contacts, auth
from src.exceptions import (
    validation_exception_handler,
    integrity_exception_handler,
    not_found_exception_handler,
    general_exception_handler,
)
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis_asyncio
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

# Включаем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Можно указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contacts.router)
app.include_router(auth.router)

app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_exception_handler)
app.add_exception_handler(HTTPException, not_found_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.get("/healthcheck")
async def healthchecker():
    return {"message": "The application is up and running!"}


@app.on_event("startup")
async def startup():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis = await redis_asyncio.from_url(redis_url, encoding="utf8", decode_responses=True)
    await FastAPILimiter.init(redis)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
