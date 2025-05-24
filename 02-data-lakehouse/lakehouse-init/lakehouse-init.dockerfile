FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /lakehouse-init
ADD . /lakehouse-init

RUN uv sync --locked

CMD ["uv", "run", "/lakehouse-init/main.py"]