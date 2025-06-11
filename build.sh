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
  mkdir -p "$CHROMEDRIVER_DIR"
  CHROME_VERSION=$("$CHROME_DIR/opt/google/chrome/google-chrome" --version | grep -oP '\d+' | head -1)
  CHROMEDRIVER_VERSION=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
  wget -O chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
  unzip chromedriver.zip -d "$CHROMEDRIVER_DIR"
  rm chromedriver.zip
else
  echo "✅ Using cached ChromeDriver"
fi
