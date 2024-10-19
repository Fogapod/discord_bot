FROM rust:1.82-alpine3.20 AS accents_builder

WORKDIR /build

COPY accents2 .

RUN : \
    && apk add --no-cache musl-dev \
    && cargo build --features cli --release

FROM python:3.12-alpine3.20

ENV PYTHONUNBUFFERED=yes \
    PYTHONDONTWRITEBYTECODE=yes \
    UV_LINK_MODE=copy

WORKDIR /code

RUN --mount=from=ghcr.io/astral-sh/uv:0.4.24,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    apk add --no-cache \
        # gif optimizer
        gifsicle \
        # Font for trocr
        ttf-dejavu \
    # export requirements from uv.lock since uv does not support sync withour venv
    && uv export --frozen --format requirements-txt --no-dev --quiet | uv pip install --system -r -

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

COPY --chown=pink:pink src src
COPY --chown=pink:pink accents2/examples accents2/examples
COPY --chown=pink:pink accents accents
COPY --chown=pink:pink schema.sql .

ENTRYPOINT ["python", "-m", "src"]
