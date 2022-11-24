FROM python:3-slim
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV LG_TESTING=false
ENTRYPOINT [ "python3", "-m", "src.main", "/data" ]
EXPOSE 8999/tcp