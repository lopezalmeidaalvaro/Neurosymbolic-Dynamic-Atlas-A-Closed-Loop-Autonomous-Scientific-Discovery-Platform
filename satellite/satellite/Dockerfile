FROM python:3.10-slim

WORKDIR /app

# Install minimal libraries
RUN pip install numpy pandas scipy scikit-learn matplotlib

# Copy codebase
COPY . .

EXPOSE 8080

CMD ["python", "satellite/cloud/deploy_saas.py", "--port", "8080"]
