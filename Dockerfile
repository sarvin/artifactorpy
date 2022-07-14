FROM python:3.8-slim-bullseye as builder
COPY requirements.txt .
ARG RUN_DEPS=""
### Required for Python modules mysqlclient and cryptography
ARG BUILD_DEPS=""

RUN apt-get update && apt-get -y upgrade && apt-get install -y ${BUILD_DEPS} \
    && apt-get update && apt-get -y upgrade && apt-get install -y ${RUN_DEPS} \
    && pip install -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge -y --auto-remove ${BUILD_DEPS}

# FROM python:3.8-slim-bullseye as app
# COPY --from=builder /root/.local /root/.local

### log messages are immediately dumped to the stream instead of being buffered.
### https://docs.python.org/3.7/using/cmdline.html#cmdoption-u
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY . /app
