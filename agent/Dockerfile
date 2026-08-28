FROM python:3-slim
WORKDIR /app

COPY agent/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY agent agent
COPY common common

ENV LG_TESTING=false
ENTRYPOINT [ "python3", "-m", "agent", "/data" ]
EXPOSE 8999/tcp