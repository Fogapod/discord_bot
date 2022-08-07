FROM python:3.10-alpine3.16

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
    # Pillow
    # refer to: https://pillow.readthedocs.io/en/stable/installation.html#external-libraries
    # and: https://github.com/python-pillow/docker-images/blob/master/alpine/Dockerfile
    zlib-dev \
    jpeg-dev \
    openjpeg-dev \
    freetype-dev \
    # gif optimizer
    gifsicle \
    # webp support
    libwebp-dev \
    # Font for trocr
    ttf-dejavu \
    && apk add --no-cache --virtual .build-deps \
    # git pip packages
    git \
    # used in uvloop ./configure
    file \
    # uvloop
    make \
    # Required for almost everything
    gcc \
    # cchardet:
    # gcc: fatal error: cannot execute 'cc1plus': execvp: No such file or directory
    g++ \
    musl-dev \
    && pip install -U pip \
    && pip install -U -r requirements.txt \
    && apk del --purge .build-deps

ARG UID=1188
ARG GID=1188

RUN addgroup -g $GID -S pink \
    && adduser -u $UID -S pink -G pink \
    && chown -R pink:pink /code

USER pink

COPY --chown=pink:pink . .

ARG GIT_BRANCH="master"
ARG GIT_COMMIT=""
ARG GIT_DIRTY="0"

ENV GIT_BRANCH=${GIT_BRANCH}
ENV GIT_COMMIT=${GIT_COMMIT}
ENV GIT_DIRTY=${GIT_DIRTY}

ENTRYPOINT ["python", "-m", "src"]
