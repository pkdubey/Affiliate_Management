# Dockerfile for Django Affiliate Management
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /code/

CMD ["gunicorn", "affiliate_management.wsgi:application", "--bind", "0.0.0.0:8000"]
