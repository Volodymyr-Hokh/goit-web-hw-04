FROM python:3.11.5

WORKDIR /app

COPY . .

EXPOSE 3000

VOLUME [ "/app/storage" ]

ENTRYPOINT ["python", "main.py"]