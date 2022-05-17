# Build Web App
# yarn build takes a long time on arm, so this step is only run in buildarch/amd64, then the
# static output is copied
FROM --platform=$BUILDPLATFORM node:lts as build_web
WORKDIR /app
COPY web web
COPY common common

WORKDIR /app/web
RUN yarn install
RUN yarn build

# Build python app
FROM python:3
WORKDIR /app

COPY api/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY api api
RUN mv api/config_docker.yaml api/config.yaml
COPY common common
COPY --from=build_web /app/web/build /app/api/static

WORKDIR /app/api
ENTRYPOINT ["python3", "-m", "src.app"]
EXPOSE 8000/tcp
