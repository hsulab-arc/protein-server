# Start with the NVIDIA PyTorch image
FROM nvidia/cuda:11.8.0-base-ubuntu22.04

# Install some basic utilities and Python
RUN apt-get -y update

RUN apt-get install -y \
    curl \
    bzip2 \
    libx11-6 \
    python3.9 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && apt-get update -y && apt-get install google-cloud-sdk -y

# Create a Python environment and install your packages
WORKDIR /app
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

# Run esmfold.py 
COPY . .