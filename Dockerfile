FROM python:3.10.12-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3-dev \
    build-essential \
    libmagic-dev \
    default-libmysqlclient-dev \
    pkg-config 

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY ./app /app

CMD ["python3", "main.py"]