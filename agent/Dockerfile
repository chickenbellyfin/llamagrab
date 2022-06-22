FROM python:3-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT [ "python3", "-m", "src.main", "/data" ]
EXPOSE 8999/tcp