FROM python:3.11-alpine3.16

ENV PYTHONUNBUFFERED=yes \
	PYTHONDONTWRITEBYTECODE=yes \
	PIP_NO_CACHE_DIR=yes \
	PIP_DISABLE_PIP_VERSION_CHECK=yes

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
	# orjson:
	# Error loading shared library libgcc_s.so.1: No such file or directory
	libgcc \
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
	# orjson
	cargo \
    && pip install -U pip \
    && pip install -U -r requirements.txt \
    && apk del --purge .build-deps

ARG UID=1188 \
	GID=1188 \
	GIT_BRANCH="master" \
	GIT_COMMIT="" \
	GIT_DIRTY="0"

ENV GIT_BRANCH=${GIT_BRANCH} \
	GIT_COMMIT=${GIT_COMMIT} \
	GIT_DIRTY=${GIT_DIRTY}

RUN addgroup -g $GID -S pink \
    && adduser -u $UID -S pink -G pink \
    && chown -R pink:pink /code

USER pink

COPY --chown=pink:pink . .

ENTRYPOINT ["python", "-m", "src"]
