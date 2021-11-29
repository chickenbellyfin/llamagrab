FROM --platform=$BUILDPLATFORM node:lts as build_web
WORKDIR /app
COPY web web
COPY common common

WORKDIR /app/web
RUN yarn install
RUN yarn build

FROM python:3
WORKDIR /app

COPY api/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=build_web /app/web/build /app/api/static
COPY api api
RUN mv api/config_docker.yaml api/config.yaml
COPY common common

WORKDIR /app/api
ENTRYPOINT ["python3", "app.py"]
EXPOSE 8000/tcp
