FROM python:3.11-slim

WORKDIR /app

# Copy minimum dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source directories and assets
COPY satellite/ /app/satellite/

# Set PYTHONPATH environment variable for relative package imports
ENV PYTHONPATH=/app

# Expose port 8000
EXPOSE 8000

# Start backend server
CMD ["uvicorn", "satellite.api.thermal_api:app", "--host", "0.0.0.0", "--port", "8000"]
