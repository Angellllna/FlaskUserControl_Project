# Використовуємо офіційний образ Python
FROM python:3.11-slim

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install poetry

RUN pip install --no-cache-dir gunicorn

COPY pyproject.toml poetry.lock README.md ./


COPY flaskusercontrol/ flaskusercontrol/



RUN poetry install


EXPOSE 5000

CMD ["poetry", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "flaskusercontrol.app:create_app()"]

