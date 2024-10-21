#!/bin/bash

CONFIG_PATH=/data/options.json

# Dropbox authentication tokens
APP_KEY=$(jq --raw-output ".app_key" $CONFIG_PATH)
APP_SECRET=$(jq --raw-output ".app_secret" $CONFIG_PATH)
REFRESH_TOKEN=$(jq --raw-output ".refresh_token" $CONFIG_PATH)

# Configuration
OUTPUT_DIR=$(jq --raw-output ".output // empty" $CONFIG_PATH)
KEEP_LAST=$(jq --raw-output ".keep_last // empty" $CONFIG_PATH)
PRESERVE_FILENAME=$(jq --raw-output ".preserve_filename // empty" $CONFIG_PATH)

# Check if empty otherwise set default
if [[ -z "$OUTPUT_DIR" ]]; then
    OUTPUT_DIR="/"
fi

# Check if empty otherwise set default
if [[ -z "$PRESERVE_FILENAME" ]]; then
    PRESERVE_FILENAME=false
fi

echo "[Info] Files will be uploaded to: ${OUTPUT_DIR}"
echo "[Info] App Key=${APP_KEY} App_Secret=${APP_SECRET} Refresh_token=${REFRESH_TOKEN}"
echo "[Info] Keep last ${KEEP_LAST} backups"
echo "[Info] Preserve filenames set to: ${PRESERVE_FILENAME}"
echo "[Info] Listening for messages via stdin service call..."

# listen for input
while read -r msg; do
    # parse JSON
    cmd="$(echo "$msg" | jq --raw-output '.command')"
    echo "[Info] Received message with command ${cmd}"
    if [[ $cmd = "upload" ]]; then

        # Upload files
        echo /upload.py "$APP_KEY" "$APP_SECRET" "$REFRESH_TOKEN" "$OUTPUT_DIR" "$PRESERVE_FILENAME"
        python3 /upload.py "$APP_KEY" "$APP_SECRET" "$REFRESH_TOKEN" "$OUTPUT_DIR" "$PRESERVE_FILENAME"

        # Remove stale backups
        if [[ "$KEEP_LAST" ]]; then
            echo "[Info] Keep last option is set, cleaning up files..."
            python3 /keep_last.py "$KEEP_LAST"
        fi

    else
        # received undefined command
        echo "[Error] Command not found: ${cmd}"
    fi

done
