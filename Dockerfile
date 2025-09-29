# pull base image
FROM python:3

# Install system dependencies FIRST
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# set working directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# install uv
RUN pip install uv

# copy uv.lock and pyproject.toml
COPY uv.lock pyproject.toml ./

# install dependencies and create virtual environment
RUN uv sync --frozen

# copy project files
COPY . .
