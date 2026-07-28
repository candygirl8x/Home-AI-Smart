# Use Python 3.12 as base
FROM python:3.12-slim

# Install SDL dependencies (for pygame)
RUN apt-get update && apt-get install -y \
    libsdl2-dev \
    libsdl2-mixer-dev \
    libsdl2-image-dev \
    libsdl2-ttf-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port (Render uses PORT environment variable)
EXPOSE 10000

# Start the application
CMD ["gunicorn", "app:app"]