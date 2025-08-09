# Dockerfile
FROM python:3.11.9-slim

WORKDIR /app

# Копируем файл с зависимостями
COPY requirements/base.txt /app/requirements/base.txt

# Обновляем pip и ставим зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements/base.txt

# Копируем весь проект внутрь контейнера
COPY . /app/

# Открываем порт 8000 для сервера
EXPOSE 8000

# Команда запуска dev-сервера Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
