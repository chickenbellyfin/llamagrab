# Build Web App
# yarn build takes a long time on arm, so this step is only run in buildarch/amd64, then the
# static output is copied
FROM --platform=$BUILDPLATFORM node:lts as build_web

# yarn install depends only on package.json and yarn.lock
# Run yarn install before copying the rest of web to avoid reinstalling if deps didnt change
WORKDIR /app/web
COPY web/package.json package.json
COPY web/yarn.lock yarn.lock
RUN yarn install

WORKDIR /app
COPY web web
COPY resources resources

WORKDIR /app/web
RUN yarn build

# Build python app
FROM python:3-slim
WORKDIR /app

COPY api/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY api api
RUN mv api/config_docker.yaml api/config.yaml
COPY resources resources
COPY --from=build_web /app/web/build /app/api/static

WORKDIR /app/api
ENTRYPOINT ["python3", "-m", "src.app"]
EXPOSE 8000/tcp
