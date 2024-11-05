FROM python:3.11

RUN apt-get update && apt-get install -y \
    python3-pip \
    libxcb-util1 \
    libgl1-mesa-dev \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xinput0 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    libxcb-render0 \
    libxcb-glx0 \
    libxi6 \
    libxkbfile1 \
    libxcb-cursor0 \
    libqt5webenginecore5 \
    libqt5webchannel5 \
    qtwebengine5-dev \
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

