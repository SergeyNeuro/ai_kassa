FROM python:3.10

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



