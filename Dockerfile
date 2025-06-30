# Use official Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.1.3

# Set working directory
WORKDIR /app

# Install Poetry
RUN pip install --upgrade pip && \
    pip install poetry==$POETRY_VERSION

# Copy project files
COPY pyproject.toml poetry.lock /app/
COPY app /app/app

# Configure Poetry to not create a virtualenv (Docker already isolates env)
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi

# Expose port
EXPOSE 8000

# Run the FastAPI app with uvicorn (dev mode with --reload)
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
