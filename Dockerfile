FROM python:3.12.2

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install requests

# Копируем весь код
COPY app/ .

CMD ["gunicorn", "--bind", "0.0.0.0:5002", "--workers", "4", "app:app"]