FROM python:3.11-slim

# Disable python buffering
ENV PYTHONUNBUFFERED=1

# Work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install python dependencies
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Create output folder
RUN mkdir -p results

# Entry command
CMD ["python", "scripts/run_all_analyses.py"]
