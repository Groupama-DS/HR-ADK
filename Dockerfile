# Use an official Python runtime as a parent image
FROM python:3.11

# Set environment variables
ENV PYTHONUNBUFFERED=True

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file and install them
# This is done in a separate step to leverage Docker's layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code into the container
COPY . .

EXPOSE 8080

CMD ["python", "app.py"]