FROM python:3.11

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libegl1-mesa \
    libglu1-mesa \
    libxkbcommon-dev \
    libglib2.0-0 \
    libxrender1 \
    libxext6 \
    libxi6 \
    libdbus-1-3 \
    libxcb1 \
    libxcb-keysyms1 \
    libxcb-cursor0 \
    && rm -rf /var/lib/apt/lists/*


# create workdir
RUN mkdir /gui_app

# set workdir
WORKDIR /gui_app

COPY requirements.txt .

# RUN pip install --no-cache-dir  -r requirements.txt
RUN pip install -r requirements.txt

# copy all files
COPY . .

