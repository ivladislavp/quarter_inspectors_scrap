# Используйте официальный образ Python
FROM python:3.10.2

# Установите рабочую директорию внутри контейнера
WORKDIR /app

# Скопируйте зависимости (если есть) в контейнер
COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install -y python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt


# Скопируйте код в контейнер
COPY .. .

# Запустите ваше приложение при старте контейнера
CMD ["python", "scrap_inspectors.py"]

# docker build -t quarterInspector_scraper .