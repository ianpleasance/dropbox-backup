import sys
import argparse
import requests
import os

import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

from pprint import pprint

TIMEOUT = 900
CHUNK_SIZE = 4 * 1024 * 1024
BASE_URL = "http://hassio/"


# Get the hassio token for authentication.
def get_headers():
    return {"X-HASSIO-KEY": os.environ.get("HASSIO_TOKEN")}


# Uploads a file to Dropbox
def upload_file(debug_info, dbx, file, target):

    # Open the file
    with open(file, 'rb') as f:

        try:
            print("[INFO] Uploading '" + file + "' to Dropbox as '" + target + "'.")

            # Get file size
            file_size = os.path.getsize(file)

            # Use normal upload method if file is small.
            if file_size <= CHUNK_SIZE:
                if debug_info is True:
                  print("[DEBUG] Using simple uploader.")

                # Use normal upload method if file is small.
                dbx.files_upload(f.read(), target, mode=WriteMode('add'))

            else:
                if debug_info is True:
                  print("[DEBUG] Using upload session.")

                upload_session_start_result = dbx.files_upload_session_start(f.read(CHUNK_SIZE))
                cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id, offset=f.tell())
                commit = dropbox.files.CommitInfo(path=target)

                while f.tell() < file_size:

                    if (file_size - f.tell()) <= CHUNK_SIZE:
                        if debug_info is True:
                          print("[DEBUG] Last chunk %s" % (file_size - f.tell()))
                        dbx.files_upload_session_finish(f.read(CHUNK_SIZE), cursor, commit)

                    else: 
                        if debug_info is True:
                          print("[DEBUG] Not last chunk %s" % (file_size - f.tell()))
                        dbx.files_upload_session_append(f.read(CHUNK_SIZE), cursor.session_id, cursor.offset)
                        cursor.offset = f.tell()
                        if debug_info is True:
                          print("[DEBUG] Cursor offset = %s" % (f.tell()))

        except ApiError as err:
            # This checks for the specific error where a user doesn't have
            # enough Dropbox space quota to upload this file
#           if (err.error.is_path() and err.error.get_path().reason.is_insufficient_space()):
#               sys.exit("[ERROR] Cannot back up; insufficient space.")
#           elif err.user_message_text:
            if err.user_message_text:
                print(err.user_message_text)
                sys.exit()
            else:
                print(err)
                sys.exit()


# Take backups from hass and define set paths.
def make_backup_path(hass_backup_list, output_dir, preserve_filename):

    upload_list = []

    for hass_backup in hass_backup_list:

        # Add extension and folder to path.
        source = hass_backup['slug'] + ".tar"
        source = os.path.join('backup', source)

        # Choose new file name
        if preserve_filename is True:
            target = hass_backup['slug'] + ".tar"
        else:
            target = hass_backup['name'] + '-' + hass_backup['date'] + ".tar"

        # Add target folder to path
        target = os.path.join(output_dir, target)

        # Add to list
        output = {'source': source, 'target': target}
        upload_list.append(output)

    return upload_list


def main(debug_info, app_key, app_secret, refresh_token, output_dir, preserve_filename):

    # Check for the key/secret/token
    if (len(app_key) == 0):
        sys.exit("[ERROR] Looks like you didn't add your app client key.")
    if (len(app_secret) == 0):
        sys.exit("[ERROR] Looks like you didn't add your app client secret.")
    if (len(refresh_token) == 0):
        sys.exit("[ERROR] Looks like you didn't add your refresh token.")

    # Get hass headers.
    my_headers = get_headers()

    # Get backup name and information as a list of dicts.
    backup_info = requests.get(BASE_URL + "backups", headers=my_headers)
    backup_info.raise_for_status()
    hass_backup_list = backup_info.json()["data"]["backups"]
    if debug_info is True:
      print("[DEBUG] hass_backup_list follows ...")
      pprint(hass_backup_list)

    # Format the file paths
    upload_list = make_backup_path(hass_backup_list, output_dir, preserve_filename)

    # Check if there are any files to upload
    if (len(upload_list) == 0):
        sys.exit("[INFO] No files found to upload.")
    else:
        print("[INFO] Found", len(upload_list), "file(s) to upload.")

    # Create an instance of a Dropbox class, which can make requests to the API.
    if debug_info is True:
      print("[DEBUG] Creating a Dropbox object. app_key=%s app_secret=%s oauth2_refresh_token=%s" % (app_key,app_secret,refresh_token))
    with dropbox.Dropbox(app_key=app_key, app_secret=app_secret, oauth2_refresh_token=refresh_token, timeout=TIMEOUT) as dbx:

        # Check that the access token is valid.
        try:
            dbx.users_get_current_account()
        except AuthError:
            sys.exit("[ERROR] Invalid refresh token; try re-generating an app secret/refresh token.")

        # Upload all files.
        for backup in upload_list:
            upload_file(debug_info, dbx, backup['source'], backup['target'])

        print("[INFO] Completed upload(s).")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Upload hassio backups.")

    parser.add_argument("debug_info", type=str, help="Debugging info.")
    parser.add_argument("app_key", type=str, help="Dropbox App client key.")
    parser.add_argument("app_secret", type=str, help="Dropbox App client secret.")
    parser.add_argument("refresh_token", type=str, help="Dropbox App refresh token.")
    parser.add_argument("output_dir", type=str, help="Output directory.")
    parser.add_argument("preserve_filename", type=str, help="Preserve original backup filename.")

    args = parser.parse_args()
    main(args.debug_info, args.app_key, args.app_secret, args.refresh_token, args.output_dir, args.preserve_filename)

