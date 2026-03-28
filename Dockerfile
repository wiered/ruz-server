FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libc6-dev libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ruz-server

ENV PYTHONUNBUFFERED=1

COPY pyproject.toml .
COPY src ./src

RUN pip install --no-cache-dir -e .

EXPOSE 2201

CMD ["python", "-m", "ruz_server.main"]
