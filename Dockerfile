# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install curl and kubectl
RUN apt-get update && apt-get install -y curl && \
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    chmod +x kubectl && mv kubectl /usr/local/bin/ && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the Python script into the container
COPY k8smonitor.py /app/k8smonitor.py

# Install necessary dependencies
RUN pip install requests Flask

# Expose port 80 for the Flask server
EXPOSE 80

# Run the Flask app when the container starts
CMD ["python", "k8smonitor.py"]
