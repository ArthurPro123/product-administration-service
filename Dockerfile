FROM python:3.11-slim

WORKDIR /app

# Create a non-root user and group
RUN useradd -m appuser && \
    chown appuser:appuser /app

# Copy requirements first
COPY --chown=appuser:appuser    requirements.txt  .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Then copy the rest of the application
COPY --chown=appuser:appuser    ./app/ .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Switch to the non-root user
USER appuser

# Run app.py when the container launches
CMD ["flask", "run", "--host", "0.0.0.0"]
