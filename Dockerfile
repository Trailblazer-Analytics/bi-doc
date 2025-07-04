FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY bidoc/ ./bidoc/
COPY setup.py .
COPY README.md .

# Install the package
RUN pip install -e .

# Create non-root user for security
RUN useradd -m -u 1000 bidoc
USER bidoc

# Set entrypoint
ENTRYPOINT ["bidoc-cli"]
CMD ["--help"]
