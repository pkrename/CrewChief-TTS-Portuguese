FROM nvidia/cuda:12.3.2-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    git \
    ffmpeg \
    libsndfile1 \
    sox \
    libsox-fmt-all \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python3 -m pip install --upgrade "pip<24.1"
RUN pip install -r requirements.txt

WORKDIR /workspace
ENTRYPOINT ["bash"]

