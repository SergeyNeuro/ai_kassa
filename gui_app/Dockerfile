FROM python:3.11

# Установка необходимых библиотек для Qt6 и xcb
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libegl1-mesa \
    libglu1-mesa \
    libxkbcommon-dev \
    libxkbcommon-x11-0 \
    libglib2.0-0 \
    libxrender1 \
    libxext6 \
    libxi6 \
    libdbus-1-3 \
    libxcb1 \
    libxcb-keysyms1 \
    libxcb-cursor0 \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-shm0 \
    libxcb-util1 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию и устанавливаем ее по умолчанию
RUN mkdir /gui_app
WORKDIR /gui_app

# Копируем и устанавливаем зависимости для Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем файлы приложения
COPY . .

