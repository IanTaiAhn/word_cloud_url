#!/usr/bin/env bash
set -o errexit

STORAGE_DIR=/opt/render/project/.render
CHROME_DIR=$STORAGE_DIR/chrome
DRIVER_DIR=$STORAGE_DIR/chromedriver

# 1. Download and extract the latest stable Chrome
if [[ ! -d "$CHROME_DIR" ]]; then
  echo "🔽 Downloading latest stable Chrome"
  LATEST_DEB_URL="https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
  mkdir -p "$CHROME_DIR"
  cd "$CHROME_DIR"
  wget -q "$LATEST_DEB_URL" -O chrome.deb
  dpkg -x chrome.deb "$CHROME_DIR"
  rm chrome.deb
else
  echo "✅ Using cached Chrome"
fi

# 2. Detect Chrome version (major.minor.patch.build—e.g., 114.0.5735.90)
FULL_VERSION=$("$CHROME_DIR/opt/google/chrome/google-chrome" --version 2>/dev/null | head -1 | grep -oP '\d+\.\d+\.\d+\.\d+')
if [[ -z "$FULL_VERSION" ]]; then
  echo "❌ Could not detect Chrome version"
  exit 1
fi
echo "➤ Detected Chrome version: $FULL_VERSION"

# Extract major version for ChromeDriver compatibility
MAJOR_VERSION=$(echo "$FULL_VERSION" | cut -d. -f1)
echo "➤ Chrome major version: $MAJOR_VERSION"

# 3. Get matching ChromeDriver version
# Note: Google deprecated the old chromedriver.storage.googleapis.com endpoints
# For Chrome 115+, use the new Chrome for Testing API
if [[ $MAJOR_VERSION -ge 115 ]]; then
  echo "➤ Using Chrome for Testing API for Chrome $MAJOR_VERSION+"
  
  # Get available versions from the new API
  AVAILABLE_VERSIONS=$(curl -sSL "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json" | \
    jq -r '.versions[] | select(.version | startswith("'$MAJOR_VERSION'.")) | .version' | \
    sort -V | tail -1)
  
  if [[ -n "$AVAILABLE_VERSIONS" ]]; then
    DRIVER_VERSION="$AVAILABLE_VERSIONS"
  else
    # Fallback to latest stable
    DRIVER_VERSION=$(curl -sSL "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json" | \
      jq -r '.channels.Stable.version')
  fi
  
  DRIVER_URL="https://storage.googleapis.com/chrome-for-testing-public/${DRIVER_VERSION}/linux64/chromedriver-linux64.zip"
else
  echo "➤ Using legacy ChromeDriver API for Chrome $MAJOR_VERSION"
  # For older Chrome versions, use the legacy API
  DRIVER_VERSION=$(curl -sSL "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$MAJOR_VERSION" 2>/dev/null || \
    curl -sSL "https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
  
  DRIVER_URL="https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip"
fi

if [[ -z "$DRIVER_VERSION" ]]; then
  echo "❌ Could not determine ChromeDriver version"
  exit 1
fi

echo "➤ Using ChromeDriver version: $DRIVER_VERSION"

# 4. Download ChromeDriver and cache it
if [[ ! -f "$DRIVER_DIR/chromedriver" ]]; then
  echo "🔽 Downloading ChromeDriver $DRIVER_VERSION"
  mkdir -p "$DRIVER_DIR"
  
  wget -q -O chromedriver.zip "$DRIVER_URL"
  
  if [[ $MAJOR_VERSION -ge 115 ]]; then
    # New format has chromedriver in a subdirectory
    unzip -q chromedriver.zip -d "$DRIVER_DIR/temp"
    mv "$DRIVER_DIR/temp/chromedriver-linux64/chromedriver" "$DRIVER_DIR/"
    rm -rf "$DRIVER_DIR/temp"
  else
    # Legacy format
    unzip -q chromedriver.zip -d "$DRIVER_DIR"
  fi
  
  rm chromedriver.zip
  chmod +x "$DRIVER_DIR/chromedriver"
else
  echo "✅ Using cached ChromeDriver"
fi

# 5. Verify installations
echo "🔍 Verifying installations..."

if [[ -x "$CHROME_DIR/opt/google/chrome/google-chrome" ]]; then
  CHROME_VERSION=$("$CHROME_DIR/opt/google/chrome/google-chrome" --version 2>/dev/null)
  echo "✅ Chrome: $CHROME_VERSION"
else
  echo "❌ Chrome installation failed"
  exit 1
fi

if [[ -x "$DRIVER_DIR/chromedriver" ]]; then
  DRIVER_VERSION_CHECK=$("$DRIVER_DIR/chromedriver" --version 2>/dev/null)
  echo "✅ ChromeDriver: $DRIVER_VERSION_CHECK"
else
  echo "❌ ChromeDriver installation failed"
  exit 1
fi

echo "✅ build.sh completed successfully"
echo "💡 Make sure to add both Chrome and ChromeDriver directories to your PATH"