# Base image
FROM python:3.10-slim

# Install MOOSE from PyPI
RUN pip install falconz

# Set working directory
WORKDIR /app

# Entry point for the MOOSE CLI
ENTRYPOINT ["falconz"]

# Default command
CMD ["-h"]
