FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies & build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    curl \
    wget \
    ca-certificates \
    ffmpeg \
    aria2 \
    mediainfo \
    pv \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Build and install Bento4 (provides mp4decrypt)
RUN git clone --depth 1 https://github.com/axiomatic-systems/Bento4.git /tmp/Bento4 && \
    cd /tmp/Bento4 && \
    mkdir cmakebuild && \
    cd cmakebuild && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    make -j$(nproc) && \
    make install && \
    rm -rf /tmp/Bento4

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy bot source code
COPY . .

# Ensure start.sh has execute permissions
RUN chmod +x start.sh

CMD ["python3", "main.py"]
