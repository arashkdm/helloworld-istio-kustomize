FROM python:3.12-slim

RUN useradd -u 10001 -m appuser
WORKDIR /app

COPY app.py /app/app.py

ENV PORT=8080
ENV MESSAGE_FILE=/etc/config/message

USER 10001:10001
EXPOSE 8080

CMD ["python", "/app/app.py"]
