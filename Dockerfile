FROM python:3.13-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy only the requirements file first to leverage Docker caching
COPY requirements.txt /app/

# Upgrade pip and setuptools to secure versions
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools>=70.0.0 && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose the application port
EXPOSE 8000

# Define the default command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
