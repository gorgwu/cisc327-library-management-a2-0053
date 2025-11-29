FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# dependencies for Playwright (and Chromium)
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    wget \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libgtk-3-0 \
    libxshmfence1 \
    libwayland-client0 \
    libwayland-cursor0 \
    xdg-utils \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN playwright install

COPY . .

ENV PLAYWRIGHT_HEADLESS=1

EXPOSE 5000

CMD ["python", "app.py"]