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

# Copy local wheel files if present (before installing dependencies)
COPY ./libs ./libs

# Install any local wheel files first
RUN if [ -d "./libs" ] && [ "$(ls -A ./libs/*.whl 2>/dev/null)" ]; then \
    uv pip install --system ./libs/*.whl; \
    fi

# Install Python dependencies from pyproject.toml using uv
RUN uv pip install --system \
    "dependency-injector>=4.48.1" \
    "fyers-apiv3>=3.1.7" \
    "logzero>=1.7.0" \
    "norenrestapipy>=0.0.22" \
    "polars>=1.32.3" \
    "pusher>=3.3.3" \
    "python-dotenv>=1.1.1" \
    "pytz>=2025.2" \
    "requests==2.31.0" \
    "smartapi-python>=1.5.5" \
    "tenacity>=9.1.2"

# Copy the entire project source code
COPY ./proalgotrader_core ./proalgotrader_core
COPY ./project ./project
COPY ./main.py ./

# Install the package itself in editable mode
RUN uv pip install --system -e .

# Create user
RUN useradd -m $USER \
    && echo "$USER:$USER" | chpasswd \
    && echo "$USER ALL=(ALL) NOPASSWD: ALL" >>/etc/sudoers

# Create file / folder permission for user
RUN chown -R $USER:$USER $WORKDIR \
    && chmod 755 $WORKDIR

# Set logged-in user
USER $USER
