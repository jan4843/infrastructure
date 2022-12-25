FROM python:3-slim
RUN apt-get update && \
    apt-get install --assume-yes --no-install-recommends \
        git \
        openssh-client \
    && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir --requirement requirements.txt && \
    cd /usr/local/lib && \
    ln -s python3.* python3
