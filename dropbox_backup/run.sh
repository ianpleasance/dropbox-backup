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
DEBUG_INFO=$(jq --raw-output ".debug_info // empty" $CONFIG_PATH)

# Check if empty otherwise set default
if [[ -z "$OUTPUT_DIR" ]]; then
    OUTPUT_DIR="/"
fi

# Check if empty otherwise set default
if [[ -z "$PRESERVE_FILENAME" ]]; then
    PRESERVE_FILENAME=false
fi

# Check if empty otherwise set default
if [[ -z "$DEBUG_INFO" ]]; then
    DEBUG_INFO=false
fi

echo "[INFO] Debug Information set to: ${DEBUG_INFO}"
echo "[INFO] Files will be uploaded to: ${OUTPUT_DIR}"
echo "[INFO] Keep last ${KEEP_LAST} backups"
echo "[INFO] Preserve filenames set to: ${PRESERVE_FILENAME}"
if [ ${DEBUG_INFO} = "true" ]
  then
    echo "[DEBUG] App Key=${APP_KEY} App_Secret=${APP_SECRET} Refresh_token=${REFRESH_TOKEN}"
fi
echo "[INFO] Listening for messages via stdin service call..."

# listen for input
while read -r msg; do
    # parse JSON
    cmd="$(echo "$msg" | jq --raw-output '.command')"
    echo "[INFO] Received message with command ${cmd}"
    if [[ $cmd = "upload" ]]; then

        # Upload files
        if [ ${DEBUG_INFO} = "true" ] 
          then
            echo "[DEBUG] python3 /upload.py ${DEBUG_INFO} ${APP_KEY} ${APP_SECRET} ${REFRESH_TOKEN} ${OUTPUT_DIR} ${PRESERVE_FILENAME}"
        fi
        python3 /upload.py "$DEBUG_INFO" "$APP_KEY" "$APP_SECRET" "$REFRESH_TOKEN" "$OUTPUT_DIR" "$PRESERVE_FILENAME"

        # Remove stale backups
        if [[ "$KEEP_LAST" ]]; then
            echo "[INFO] Keep last option is set, cleaning up files..."
            if [ ${DEBUG_INFO} = "true" ]
              then
                echo "[DEBUG] python3 /keep_last.py ${DEBUG_INFO} ${KEEP_LAST}"
            fi
            python3 /keep_last.py "$DEBUG_INFO" "$KEEP_LAST"
        fi

    else
        # received undefined command
        echo "[ERROR] Command not found: ${cmd}"
    fi

done
