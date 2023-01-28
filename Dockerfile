FROM python:3-slim
RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
        git='*' \
        make='*' \
        openssh-client='*' \
    && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir --requirement requirements.txt && \
    ln -s /usr/local/lib/python3.* /usr/local/lib/python3
