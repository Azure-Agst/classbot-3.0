# Source our image from python, buster
FROM python:3.10.5-slim-bullseye

# Set Working Dir
WORKDIR /usr/src/app

# Copy in app and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Set default env vars
ENV DOCKER_ENV=True

# Set Labels
LABEL org.opencontainers.image.authors="me@azureagst.dev"
LABEL org.opencontainers.image.source="https://github.com/azure-agst/classbot-3.0"

# Set entrypoint
CMD [ "python3", "-m", "classbot" ]
