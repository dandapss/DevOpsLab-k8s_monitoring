FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Keep the tested pure helpers alongside the exporter entry point.
COPY src/ .

EXPOSE 8080

CMD ["python", "main.py"]
