FROM python:3.12-slim

WORKDIR /app

COPY homework8.py .

CMD ["python", "-u", "homework8.py"]
