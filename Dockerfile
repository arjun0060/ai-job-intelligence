FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.docker.txt .

RUN pip install \
    --no-cache-dir \
    --default-timeout=300 \
    --retries 5 \
    --index-url https://download.pytorch.org/whl/cpu \
    torch==2.14.0+cpu

RUN pip install \
    --no-cache-dir \
    --default-timeout=300 \
    --retries 5 \
    -r requirements.docker.txt

RUN playwright install --with-deps chromium

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]