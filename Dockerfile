FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости отдельно — чтобы Docker кэшировал этот слой
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

CMD ["python", "main.py"]
