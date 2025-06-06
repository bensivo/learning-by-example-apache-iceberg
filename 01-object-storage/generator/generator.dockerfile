FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /generator
WORKDIR /generator

RUN uv sync --locked

CMD ["uv", "run", "/generator/main.py"]