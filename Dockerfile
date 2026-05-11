FROM cloakhq/cloakbrowser

WORKDIR /app

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh

COPY pyproject.toml uv.lock ./

RUN uv sync --no-dev --frozen --no-cache

COPY . .

RUN chmod +x start.sh docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]