FROM python:3.12-slim-bookworm

WORKDIR /app

# CloakBrowser downloads its free Chromium build here (no license key needed).
# A fixed location keeps the build-time download available at runtime.
ENV CLOAKBROWSER_CACHE_DIR=/opt/cloakbrowser

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh

COPY pyproject.toml uv.lock ./

RUN uv sync --no-dev --frozen --no-cache

# System libraries Chromium needs (installed via Playwright's dependency helper)
RUN uv run playwright install-deps chromium

COPY . .

RUN chmod +x start.sh docker-entrypoint.sh

# Pre-download the free CloakBrowser Chromium so the first request is fast and
# the build fails loudly if the binary cannot be fetched.
RUN uv run python -c "from cloakbrowser import ensure_binary; print('CloakBrowser binary:', ensure_binary())"

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
