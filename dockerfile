# base Playwright image (noble) – does **not** include Python
FROM mcr.microsoft.com/playwright:v1.58.2-noble

WORKDIR /app

COPY requirements.txt .

USER root

# install Python and pip, then install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# copy application and entrypoint
COPY . .

# ensure scripts are executable
RUN chmod +x start.sh docker-entrypoint.sh

# keep root so entrypoint can chown volume
EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]