FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py gunicorn_config.py ./
COPY templates/ templates/
COPY static/ static/

# Create data directory for SQLite
RUN mkdir -p /app/data

# Set environment variables
ENV FLASK_APP=app.py
ENV SECRET_KEY=change-me-in-production

EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "-c", "gunicorn_config.py", "app:app"]
