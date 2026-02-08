FROM python:3.12-slim

RUN useradd -u 10002 -m controller
WORKDIR /app

RUN pip install --no-cache-dir kubernetes

COPY controller.py /app/controller.py

USER 10002:10002
CMD ["python", "/app/controller.py"]
