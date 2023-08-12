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

# Build web2
FROM --platform=$BUILDPLATFORM node:lts as build_web2
WORKDIR /app/web2
COPY web2/package.json package.json
COPY web2/yarn.lock yarn.lock
RUN yarn install

WORKDIR /app
COPY web2 web2

WORKDIR /app/web2
RUN yarn build

# Build python app
FROM python:3-slim
WORKDIR /app

COPY api/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip freeze > pip-freeze.txt

COPY api api
COPY common common
COPY config config
COPY resources resources
COPY --from=build_web /app/web/build /app/static

# web2
COPY web2 web2
COPY --from=build_web2 /app/web2/static web2/static

RUN mv config/config_docker.yaml config/config.yaml

ENTRYPOINT ["python3", "-m", "api"]
EXPOSE 8000/tcp
