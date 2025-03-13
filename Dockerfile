# Використовуємо офіційний образ Python
FROM python:3.11-slim

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install poetry

# Копіюємо файли в контейнер
COPY pyproject.toml poetry.lock README.md ./


COPY flaskusercontrol/ flaskusercontrol/



# Встановлюємо Poetry та залежності
RUN poetry install


# Виставляємо порт Flask
EXPOSE 5000

# Запускаємо додаток
CMD ["poetry", "run", "python", "flaskusercontrol/app.py"]
