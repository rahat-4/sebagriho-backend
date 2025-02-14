FROM python:3.12-alpine

WORKDIR /app

# # Install system dependencies for Python packages
# RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev \
#     postgresql-dev mariadb-dev build-base

COPY ../requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY ../ /app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
