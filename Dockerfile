# Base image
FROM python:3.13-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies for building Python packages & Postgres
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files (production only)
RUN python core/manage.py collectstatic --noinput

# Expose port 8000
EXPOSE 8000

# Default command (production)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
