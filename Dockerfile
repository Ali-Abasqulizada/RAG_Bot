# Use a lightweight Python version
FROM python:3.11-slim

# Hugging Face Spaces requires a non-root user with ID 1000
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Set the working directory
WORKDIR /home/user/app

# Copy requirements and install them
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your project files
COPY --chown=user . .

# Collect static files for the UI
RUN python manage.py collectstatic --noinput

# Expose port 7860 (Hugging Face's default port)
EXPOSE 7860

# Start the Gunicorn server
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:7860", "--workers", "1", "--threads", "2"]