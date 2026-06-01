FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements from root or custom local dependencies
COPY api/requirements.txt ./

# Install packages
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir psycopg2-binary redis pyjwt[crypto] bcrypt

# Copy scientific libraries and controllers
COPY . .

# Set Python search path to import root modules
ENV PYTHONPATH=/app

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/v1/health || exit 1

CMD ["uvicorn", "api.thermal_api:app", "--host", "0.0.0.0", "--port", "8000"]
