#!/usr/bin/env bash
set -o errexit

STORAGE_DIR=/opt/render/project/.render
CHROME_DIR=$STORAGE_DIR/chrome
DRIVER_DIR=$STORAGE_DIR/chromedriver

# 1. Download and extract the latest stable Chrome
if [[ ! -d "$CHROME_DIR" ]]; then
  echo "🔽 Downloading latest stable Chrome"
  LATEST_DEB_URL=$(curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb)
  mkdir -p "$CHROME_DIR"
  cd "$CHROME_DIR"
  wget -q "$LATEST_DEB_URL" -O chrome.deb
  dpkg -x chrome.deb "$CHROME_DIR"
  rm chrome.deb
else
  echo "✅ Using cached Chrome"
fi

# 2. Detect Chrome version (major.minor.patch.build—e.g., 114.0.5735.90)
FULL_VERSION=$("$CHROME_DIR/opt/google/chrome/google-chrome" --version | head -1 | grep -oP '\d+\.\d+\.\d+\.\d+')
if [[ -z "$FULL_VERSION" ]]; then
  echo "❌ Could not detect Chrome version"
  exit 1
fi
echo "➤ Detected Chrome version: $FULL_VERSION"

# 3. Get matching ChromeDriver version (latest for this Chrome release)
DRIVER_VERSION=$(curl -sSL "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$FULL_VERSION")
if [[ -z "$DRIVER_VERSION" ]]; then
  echo "✅ No exact match; falling back to latest ChromeDriver"
  DRIVER_VERSION=$(curl -sSL "https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
fi
echo "➤ Using ChromeDriver version: $DRIVER_VERSION"

# 4. Download ChromeDriver and cache it
if [[ ! -f "$DRIVER_DIR/chromedriver" ]]; then
  mkdir -p "$DRIVER_DIR"
  wget -q -O chromedriver.zip "https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip"
  unzip -q chromedriver.zip -d "$DRIVER_DIR"
  rm chromedriver.zip
else
  echo "✅ Using cached ChromeDriver"
fi

echo "✅ build.sh completed successfully"


# #!/usr/bin/env bash
# set -o errexit

# STORAGE_DIR=/opt/render/project/.render
# CHROME_DIR=$STORAGE_DIR/chrome
# CHROMEDRIVER_DIR=$STORAGE_DIR/chromedriver

# # Install Chrome if not already cached
# if [[ ! -d "$CHROME_DIR" ]]; then
#   echo "🔽 Downloading Chrome"
#   mkdir -p "$CHROME_DIR"
#   cd "$CHROME_DIR"
#   wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
#   dpkg -x google-chrome-stable_current_amd64.deb "$CHROME_DIR"
#   rm google-chrome-stable_current_amd64.deb
# else
#   echo "✅ Using cached Chrome"
# fi

# # Install ChromeDriver if not already cached
# if [[ ! -d "$CHROMEDRIVER_DIR" ]]; then
#   echo "🔽 Downloading ChromeDriver"
# #   mkdir -p "$CHROMEDRIVER_DIR"

# #   CHROME_VERSION=$("$CHROME_DIR/opt/google/chrome/google-chrome" --version | grep -oP '\d+' | head -1)
# #   echo "➤ Chrome version detected: $CHROME_VERSION"

# #   CHROMEDRIVER_VERSION=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")

# #   wget -O chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
# #   unzip chromedriver.zip -d "$CHROMEDRIVER_DIR"
# #   rm chromedriver.zip
# #   echo "➤ ChromeDriver version to download: $CHROMEDRIVER_VERSION"

#   #Pinned Chrome and Driver version
#   CHROME_VERSION=114.0.5735.90
  
#   # Install Chrome
#   wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}-1_amd64.deb
#   dpkg -x google-chrome-stable_${CHROME_VERSION}-1_amd64.deb "$CHROME_DIR"
#   rm google-chrome-stable_${CHROME_VERSION}-1_amd64.deb
#   echo "➤ Chrome version installed: $CHROME_VERSION"

#   # Download matching ChromeDriver
#   wget -O chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip"
#   unzip chromedriver.zip -d "$CHROMEDRIVER_DIR"
#   rm chromedriver.zip
#   echo "➤ Chromedriver matched version installed: $CHROME_VERSION"
# else
#   echo "✅ Using cached ChromeDriver"
# fi
