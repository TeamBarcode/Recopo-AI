FROM python:3.13.2-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m pip install --upgrade pip \
    && python -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.13.0 \
    && python -m pip install -r requirements.txt

COPY app ./app
COPY scripts ./scripts

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
