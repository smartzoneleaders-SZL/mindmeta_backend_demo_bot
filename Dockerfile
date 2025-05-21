# Choose our version of Python
FROM python:3.12

# Install system-level dependencies for PyAudio
RUN apt-get update && apt-get install -y \
    build-essential \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up a working directory
WORKDIR /code

# Copy requirements first
COPY ./requirements.txt /code/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the rest of the code (including setup.py, app/, etc.)
COPY . /code

# ✅ Copy the .env file into the image
COPY .env /code/.env

# Install your custom library in editable mode
RUN pip install -e .

# ✅ Add app/ to PYTHONPATH so 'routes' and other modules can be found
ENV PYTHONPATH="/code/app"

# Start the FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
