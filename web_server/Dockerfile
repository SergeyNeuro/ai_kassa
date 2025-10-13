FROM python:3.12

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# create workdir
RUN mkdir /ai_kassa_web_app

# set workdir
WORKDIR /ai_kassa_web_app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
# RUN pip install --upgrade pip


# RUN pip install --no-cache-dir  -r requirements.txt
RUN pip install -r requirements.txt


# copy all files
COPY . .



