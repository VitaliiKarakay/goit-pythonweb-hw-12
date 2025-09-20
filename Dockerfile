FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY .env.example .env

ENV DATABASE_URL=postgresql://postgres:password@localhost:5432/hw8
ENV REDIS_URL=redis://localhost:6379/0
ENV JWT_SECRET_KEY=your_jwt_secret_key
ENV JWT_ALGORITHM=HS256
ENV ACCESS_TOKEN_EXPIRE_MINUTES=30
ENV CLOUDINARY_URL=cloudinary://your_cloudinary_key:your_cloudinary_secret@your_cloudinary_cloud_name

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
