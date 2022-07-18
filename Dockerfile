# Source our image from python, buster
FROM python:3.10.5-bullseye

# Install the latest version of Firefox
RUN export DEBIAN_FRONTEND=noninteractive \
  # Install dependencies
  && apt-get update \
  && apt-get install --no-install-recommends --no-install-suggests -y \
    libxtst6 \
    libgtk-3-0 \
    libx11-xcb-dev \
    libdbus-glib-1-2 \
    libxt6 \
    libpci-dev \
    bzip2 \
    libasound2 \
  # Install Firefox
  && DL='https://download.mozilla.org/?product=firefox-latest-ssl&os=linux64' \
  && curl -sL "$DL" | tar -xj -C /opt \
  && ln -s /opt/firefox/firefox /usr/local/bin/ \
  # Remove obsolete files
  && apt-get autoremove --purge -y \
    bzip2 \
  && apt-get clean \
  && rm -rf \
    /tmp/* \
    /usr/share/doc/* \
    /var/cache/* \
    /var/lib/apt/lists/* \
    /var/tmp/*

# Install the latest version of Geckodriver
RUN BASE_URL=https://github.com/mozilla/geckodriver/releases/download \
  && VERSION=$(curl -sL \
    https://api.github.com/repos/mozilla/geckodriver/releases/latest | \
    grep tag_name | cut -d '"' -f 4) \
  && curl -sL "$BASE_URL/$VERSION/geckodriver-$VERSION-linux64.tar.gz" | \
    tar -xz -C /usr/local/bin

# Set Working Dir
WORKDIR /usr/src/app

# Copy in app and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Set env vars
ENV DOCKER_ENV=True

# Set Labels
LABEL org.opencontainers.image.authors="me@azureagst.dev"
LABEL org.opencontainers.image.source="https://github.com/azure-agst/classbot-3.0"

# Set entrypoint
CMD [ "python3", "-m", "fsu-classbot" ]
