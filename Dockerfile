FROM mcr.microsoft.com/playwright:v1.58.2-noble

WORKDIR /app

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip curl && \
    rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh

COPY pyproject.toml uv.lock ./

RUN uv sync --no-dev --frozen --no-cache

COPY . .

RUN chown -R pwuser:pwuser /app && chmod +x start.sh docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]