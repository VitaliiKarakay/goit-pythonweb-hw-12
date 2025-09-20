FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY .env.example .env

ENV DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/hw8
ENV REDIS_URL=redis://redis:6379/0
ENV JWT_SECRET_KEY=your_jwt_secret_key
ENV JWT_ALGORITHM=HS256
ENV ACCESS_TOKEN_EXPIRE_MINUTES=30
ENV CLOUDINARY_URL=cloudinary://your_cloudinary_key:your_cloudinary_secret@your_cloudinary_cloud_name

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
