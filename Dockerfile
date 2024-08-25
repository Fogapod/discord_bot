FROM rust:1.80-alpine3.20 as accents_builder

WORKDIR /build

COPY accents2 .

RUN : \
    && apk add --no-cache musl-dev \
    && cargo build --features cli --release

FROM python:3.12-alpine3.20

ENV PYTHONUNBUFFERED=yes \
    PYTHONDONTWRITEBYTECODE=yes

WORKDIR /code

COPY --from=ghcr.io/astral-sh/uv:0.3.3 /uv /bin/uv
COPY uv.lock .
COPY pyproject.toml .

RUN : \
    && apk add --no-cache \
        # gif optimizer
        gifsicle \
        # Font for trocr
        ttf-dejavu \
    && uv sync --frozen --no-cache --no-dev \
    && rm /bin/uv

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
RUN rm uv.lock pyproject.toml

ENTRYPOINT ["/code/.venv/bin/python", "-m", "src"]
