FROM ubuntu:latest

# Prevent interactive prompts during apt install
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install Python and venv support
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip python3-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python3 -m venv /app/venv

# Put the venv's bin directory on PATH so all subsequent
# RUN / ENTRYPOINT / CMD calls use the venv Python & packages
ENV PATH="/app/venv/bin:$PATH"

# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt

# Copy the rest of the application code
COPY . .

EXPOSE 8000

# Start the FastAPI app via uvicorn (resolved from the venv)
#ENTRYPOINT is not mutable after the image is built
#Best practice is to put executable commands in the ENTRYPOINT and configuration options in CMD
ENTRYPOINT ["uvicorn"]
#CMD is mutable and can be overridden
CMD ["main:app", "--host", "0.0.0.0", "--port", "8000"]