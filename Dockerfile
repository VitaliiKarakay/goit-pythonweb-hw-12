FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV DATABASE_URL=postgresql://postgres:password@localhost:5432/hw8

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
