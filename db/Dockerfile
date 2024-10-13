# Use a lightweight base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /db

# Copy the source code
COPY ./db/requirements.txt .

# Install required libraries
RUN pip install -r requirements.txt

# Expose the API port (change if needed)
EXPOSE 5000

# Command to run the application
ENTRYPOINT ["python", "vector_db.py"]
