# Use a lightweight Python image 
FROM python:3.10-slim 

# Set environment variables to prevent Python from writing .pyc files & Ensure Python output is not buffered
# (यहाँ से बैकस्लैश हटा दिया गया है और PYTHONUNBUFFERED भी जोड़ दिया गया है)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required by LightGBM
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the application code
COPY . .


# Install the package in editable mode
RUN pip install -r requirements.txt
# Train the model before running the application

# Expose the port that Flask will run ong
EXPOSE 5000

# Command to run the app
CMD ["python", "application.py"]



