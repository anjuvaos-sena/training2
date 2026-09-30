FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBUG=False \
    PORT=10000

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN DEBUG=True python manage.py collectstatic --noinput

EXPOSE 10000

CMD ["sh", "/app/docker-entrypoint.sh"]