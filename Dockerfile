FROM python:3.9-alpine3.12

ARG UID=1000
ARG GID=1000

# enables proper stdout flushing
ENV PYTHONUNBUFFERED yes
# no .pyc files
ENV PYTHONDONTWRITEBYTECODE yes

# pip optimizations
ENV PIP_NO_CACHE_DIR yes
ENV PIP_DISABLE_PIP_VERSION_CHECK yes

WORKDIR /code

COPY requirements.txt .

RUN apk add --no-cache \
    git \
    # Pillow
    # refer to: https://pillow.readthedocs.io/en/stable/installation.html#external-libraries
    # and: https://github.com/python-pillow/docker-images/blob/master/alpine/Dockerfile
    zlib-dev \
    jpeg-dev \
    openjpeg-dev \
    freetype-dev \
    # Font for trocr
    ttf-dejavu \
    && apk add --no-cache --virtual .build-deps \
    # Required for almost everything
    gcc \
    musl-dev \
    && pip install -U pip \
    && pip install -U -r requirements.txt \
    && apk del --purge .build-deps

RUN addgroup -g $GID -S pink \
    && adduser -u $UID -S pink -G pink \
    && chown -R pink:pink /code

USER pink

COPY --chown=pink:pink pink pink
COPY --chown=pink:pink dbschema dbschema

ENTRYPOINT ["python", "-m", "pink"]
