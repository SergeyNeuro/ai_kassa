FROM python:3.11

RUN apt-get update && apt-get install -y \
    libxcb1 \
    libxkbcommon-x11-0 \
    libx11-xcb1 \
    libgl1-mesa-glx \
    libegl1-mesa \  # Добавлено для поддержки EGL
    libxi6 \
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

