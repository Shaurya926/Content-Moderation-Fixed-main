# Content Moderation OpenEnv — Dockerfile
# Compatible with Hugging Face Spaces (port 7860)

FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies directly (no uv needed in container)
RUN pip install --no-cache-dir \
    "openenv-core>=0.2.0" \
    "fastapi>=0.100.0" \
    "uvicorn[standard]>=0.23.0" \
    "pydantic>=2.0.0" \
    "openai>=1.0.0" \
    "httpx>=0.24.0" \
    "requests>=2.31.0"

# Copy ALL project files
COPY pyproject.toml ./
COPY openenv.yaml ./
COPY app.py ./
COPY inference.py ./
COPY README.md ./
COPY env/ ./env/
COPY server/ ./server/

# HF Spaces uses port 7860
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -sf http://localhost:7860/health || exit 1

# Start server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
