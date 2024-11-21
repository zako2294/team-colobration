# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install dependencies from requirements.txt
RUN pip install -r requirements.txt

# Install Gunicorn as the web server
RUN pip install gunicorn

# Expose port 80 for Heroku
EXPOSE 80

# Command to run the app using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:80", "main:app"]
