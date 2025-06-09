FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies - ensure all packages are architecture compatible
RUN pip install --no-cache-dir -r requirements.txt

# Install additional system dependencies if needed for cross-architecture compatibility
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the rest of the application
COPY . .

# Make port 8501 available for Streamlit
EXPOSE 8501

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Command to run the app
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
