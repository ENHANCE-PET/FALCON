# Base image
FROM python:3.11-slim

# Build the reviewed source, so release images include the security fixes.
COPY . /tmp/falconz
RUN pip install --no-cache-dir /tmp/falconz

# Set working directory
WORKDIR /app

# Entry point for the FalconZ CLI
ENTRYPOINT ["falconz"]

# Default command
CMD ["-h"]
