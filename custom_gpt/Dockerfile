# Use official Python image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv or use pip + requirements.txt
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy project files
COPY . .

RUN cd custom_gpt


# Expose port (default for Django or Gunicorn)
EXPOSE 8000

# Collect static files (optional — required for production)
#CMD python manage.py collectstatic --noinput

# Run Gunicorn (for production)
ENTRYPOINT ["python", "manage.py", "migrate", "&&", "python", "manage.py", "runserver", "0.0.0.0:8000"]

