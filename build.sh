#!/usr/bin/env bash
set -o errexit

STORAGE_DIR=/opt/render/project/.render
CHROME_DIR=$STORAGE_DIR/chrome
CHROMEDRIVER_DIR=$STORAGE_DIR/chromedriver

# Install Chrome if not already cached
if [[ ! -d "$CHROME_DIR" ]]; then
  echo "🔽 Downloading Chrome"
  mkdir -p "$CHROME_DIR"
  cd "$CHROME_DIR"
  wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  dpkg -x google-chrome-stable_current_amd64.deb "$CHROME_DIR"
  rm google-chrome-stable_current_amd64.deb
else
  echo "✅ Using cached Chrome"
fi

# Install ChromeDriver if not already cached
if [[ ! -d "$CHROMEDRIVER_DIR" ]]; then
  echo "🔽 Downloading ChromeDriver"
#   mkdir -p "$CHROMEDRIVER_DIR"

#   CHROME_VERSION=$("$CHROME_DIR/opt/google/chrome/google-chrome" --version | grep -oP '\d+' | head -1)
#   echo "➤ Chrome version detected: $CHROME_VERSION"

#   CHROMEDRIVER_VERSION=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")

#   wget -O chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
#   unzip chromedriver.zip -d "$CHROMEDRIVER_DIR"
#   rm chromedriver.zip
#   echo "➤ ChromeDriver version to download: $CHROMEDRIVER_VERSION"

  #Pinned Chrome and Driver version
  CHROME_VERSION=114.0.5735.90
  
  # Install Chrome
  wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}-1_amd64.deb
  dpkg -x google-chrome-stable_${CHROME_VERSION}-1_amd64.deb "$CHROME_DIR"
  rm google-chrome-stable_${CHROME_VERSION}-1_amd64.deb
  echo "➤ Chrome version installed: $CHROME_VERSION"

  # Download matching ChromeDriver
  wget -O chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip"
  unzip chromedriver.zip -d "$CHROMEDRIVER_DIR"
  rm chromedriver.zip
  echo "➤ Chromedriver matched version installed: $CHROME_VERSION"
else
  echo "✅ Using cached ChromeDriver"
fi
