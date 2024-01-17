FROM alpine:3.18 as accents_builder

WORKDIR /build

COPY accents2 .

RUN : \
    && apk add cargo libgcc \
    && cargo build --features cli --release

FROM python:3.11-alpine3.18

ENV PYTHONUNBUFFERED=yes \
    PYTHONDONTWRITEBYTECODE=yes \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore

WORKDIR /code

COPY requirements.txt .

RUN : \
    && apk add --no-cache \
        # gif optimizer
        gifsicle \
        # Font for trocr
        ttf-dejavu \
    && pip install -U pip \
    && pip install -r requirements.txt \
    && rm requirements.txt

COPY --from=accents_builder /build/target/release/pink_accents /usr/bin/pink_accents

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
