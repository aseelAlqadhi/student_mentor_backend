# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all app code
COPY . .

# Expose the port (Cloud Run will set the PORT environment variable)
EXPOSE 8080

# Run the app with gunicorn using the PORT environment variable
# Cloud Run will set PORT automatically, defaulting to 8080 if not set
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 4 --worker-class uvicorn.workers.UvicornWorker --timeout 0 app.main:app