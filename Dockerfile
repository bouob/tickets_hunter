FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TICKETS_HUNTER_XVFB=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        fonts-liberation \
        libasound2 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libcairo2 \
        libcups2 \
        libdbus-1-3 \
        libdrm2 \
        libexpat1 \
        libgbm1 \
        libglib2.0-0 \
        libgtk-3-0 \
        libnss3 \
        libpango-1.0-0 \
        libx11-6 \
        libxcb1 \
        libxcomposite1 \
        libxdamage1 \
        libxext6 \
        libxfixes3 \
        libxkbcommon0 \
        libxrandr2 \
        libxshmfence1 \
        libxss1 \
        libxtst6 \
        unzip \
        xauth \
        xvfb \
    && rm -rf /var/lib/apt/lists/*

COPY requirement.txt ./
RUN python -m pip install --upgrade pip \
    && pip install -r requirement.txt

COPY . .
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /data \
    && mkdir -p /tmp/.X11-unix \
    && chmod 1777 /tmp/.X11-unix \
    && chown -R appuser:appuser /app /data

USER appuser
WORKDIR /app/src

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["python", "settings.py"]
