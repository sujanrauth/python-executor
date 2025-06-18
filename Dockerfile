# Dockerfile for nsjail container
FROM ubuntu:22.04

# Install dependencies and requirements for nsjail and Python
RUN apt-get update && apt-get install -y \
    autoconf \
    bison \
    flex \
    gcc \
    g++ \
    git \
    libprotobuf-dev \
    libnl-route-3-dev \
    libtool \
    make \
    pkg-config \
    protobuf-compiler \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Clone and build nsjail from source
WORKDIR /opt
RUN git clone https://github.com/google/nsjail.git
WORKDIR /opt/nsjail
RUN make

# Make nsjail available system-wide in PATH
RUN cp nsjail /usr/local/bin/

# Set working directory for the application
WORKDIR /app

# Copy requirements into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy main application files
COPY app.py .

# Expose the port that the Flask application listens
EXPOSE 8080

# Command to execute when container starts
CMD ["python3", "app.py"]