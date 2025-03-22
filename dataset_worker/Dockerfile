FROM python:3.10

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# create workdir
RUN mkdir /src

# set workdir
WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .


RUN pip install --upgrade pip
RUN pip install -r requirements.txt


# copy all files
COPY . .



