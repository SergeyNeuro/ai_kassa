FROM python:3.11

# Установка зависимостей для Qt и Xvfb
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
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-shm0 \
    libxcb-util1 \
    libxcb-xfixes0 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Установка переменных окружения для Qt
ENV QT_QPA_PLATFORM_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt5/plugins/platforms
ENV QT_DEBUG_PLUGINS=1

# Создаем рабочую директорию и устанавливаем ее по умолчанию
RUN mkdir /gui_app
WORKDIR /gui_app

# Копируем и устанавливаем зависимости для Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем файлы приложения
COPY . .

