FROM python:3.13.11-alpine3.23

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "docker_client.py"]
