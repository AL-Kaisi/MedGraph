# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies from requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port 8501 for Flask
EXPOSE 8501

# Run the Flask app
CMD ["python", "app/flask_app.py"]