FROM python:3.12

# create workdir
RUN mkdir /admin_app

# set workdir
WORKDIR /admin_app

COPY requirements.txt .

# RUN pip install --no-cache-dir  -r requirements.txt
RUN pip install -r requirements.txt

# copy all files
COPY . .

# CMD gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:7770
