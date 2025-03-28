# Use an official Python runtime as a parent image.
# The python:3.10-slim image supports ARM on Mac.
FROM python:3.10-slim

# Set environment variables:
# Prevents Python from writing pyc files and forces stdout/stderr to be unbuffered.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container.
WORKDIR /app

# Copy only the requirements.txt first to leverage Docker cache.
COPY requirements.txt /app/

# Upgrade pip and install the dependencies from requirements.txt.
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project code to the working directory.
COPY . /app/

# Expose port 8000 for the Django development server.
EXPOSE 8000

# Define the default command to run the Django development server.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
