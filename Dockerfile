# Use the official Python image for Python 3.13
FROM python:3.13

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV DEBCONF_NOWARNINGS=yes
ENV PIP_ROOT_USER_ACTION=ignore
ENV PROALGOTRADER_DOCKER=true

ARG USER=proalgotrader
ARG WORKDIR=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sudo \
    nano \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for dependency management
RUN pip install --no-cache-dir uv

# Set work directory
WORKDIR $WORKDIR

# Copy dependency files first (for better caching)
COPY pyproject.toml ./
COPY uv.lock* ./

# Install dependencies (cached layer)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# Copy the project files
COPY ./project ./project
COPY ./main.py ./

# Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Create user
RUN useradd -m $USER \
    && echo "$USER:$USER" | chpasswd \
    && echo "$USER ALL=(ALL) NOPASSWD: ALL" >>/etc/sudoers

# Create file / folder permission for user
RUN chown -R $USER:$USER $WORKDIR \
    && chmod 755 $WORKDIR

# Set logged-in user
USER $USER
