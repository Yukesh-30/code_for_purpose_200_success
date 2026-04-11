# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (required for psycopg2 and others if needed)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port (Render/Railway use PORT env var, but 5000 is default)
EXPOSE 5000

# Start server using gunicorn
CMD gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} main:app
