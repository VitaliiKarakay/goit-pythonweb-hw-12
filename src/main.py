from fastapi import FastAPI, HTTPException
from src.api import contacts
from src.exceptions import (
    validation_exception_handler,
    integrity_exception_handler,
    not_found_exception_handler,
    general_exception_handler,
)
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

app = FastAPI()

app.include_router(contacts.router)

app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_exception_handler)
app.add_exception_handler(HTTPException, not_found_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.get("/healthcheck")
async def healthchecker():
    return {"message": "The application is up and running!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
