FROM python:3.12-alpine

# Set working directory
WORKDIR /app

# Install system dependencies and security updates
RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    linux-headers \
    && apk upgrade --no-cache

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && pip cache purge

# Copy application code
COPY bidoc/ ./bidoc/
COPY setup.py .
COPY README.md .

# Install the package
RUN pip install --no-cache-dir -e . \
    && pip cache purge

# Create non-root user for security with restricted permissions
RUN addgroup -g 1000 bidoc \
    && adduser -D -u 1000 -G bidoc bidoc \
    && chown -R bidoc:bidoc /app
USER bidoc

# Add security labels
LABEL security.non-root=true
LABEL security.updated="2025-07-04"

# Set entrypoint
ENTRYPOINT ["bidoc-cli"]
CMD ["--help"]
