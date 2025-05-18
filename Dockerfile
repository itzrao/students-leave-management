# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (e.g., 5000 for Flask, change if needed)
EXPOSE 5000

# Command to run app
CMD ["python", "app.py"]
