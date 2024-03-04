FROM rust:alpine as accents_builder

WORKDIR /build

COPY accents2 .

RUN : \
    && apk add --no-cache musl-dev \
    && cargo build --features cli --release

FROM python:3.11-alpine3.19

ENV PYTHONUNBUFFERED=yes \
    PYTHONDONTWRITEBYTECODE=yes \
    PIP_ROOT_USER_ACTION=ignore

WORKDIR /code

COPY requirements/base.txt requirements.txt

RUN : \
    && apk add --no-cache \
        # gif optimizer
        gifsicle \
        # Font for trocr
        ttf-dejavu \
    && pip install uv --no-cache-dir --disable-pip-version-check \
    && uv pip install -r requirements.txt --no-cache --system \
    && uv pip uninstall uv --system \
    && rm requirements.txt

COPY --from=accents_builder /build/target/release/sayit /usr/bin/sayit

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
