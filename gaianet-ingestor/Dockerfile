FROM python:3.9-slim

# Create working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . .

# Cloud Run uses $PORT
ENV PORT=8080

# Expose port (optional for Cloud Run but useful locally)
EXPOSE 8080

# Run Flask app
CMD ["python", "main.py"]
