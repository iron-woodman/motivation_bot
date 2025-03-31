# Многоступенчатая сборка для бота

# Этап 1: Сборка зависимостей
FROM python:3.13-slim-bullseye AS builder
WORKDIR /tmp/motivation_bot  # Уникальное имя рабочей директории
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Этап 2: Финальный образ
FROM python:3.13-slim-bullseye
WORKDIR /motivation_bot # Уникальное имя рабочей директории для второго бота
COPY . .  # Копируем все файлы проекта, включая .env
COPY --from=builder /tmp/motivation_bot/ .

CMD ["python3", "bot.py"]
