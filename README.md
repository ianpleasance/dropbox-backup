# Home Assistant add-on: Dropbox backup

[![Last commit](https://img.shields.io/github/last-commit/mikevansighem/dropbox-backup?style=flat-square)](https://github.com/mikevansighem/dropbox-backup/commits/main)
[![Commits per month](https://img.shields.io/github/commit-activity/m/mikevansighem/dropbox-backup?style=flat-square)](https://github.com/mikevansighem/dropbox-backup/commits/main)
[![License](https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square)](https://github.com/mikevansighem/dropbox-backup/blob/main/LICENSE.md)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/mikevansighem/dropbox-backup/.github/workflows/ci.yaml?branch=main?style=flat-square)](https://github.com/mikevansighem/dropbox-backup/actions)
[![GitHub issues](https://img.shields.io/github/issues-raw/mikevansighem/dropbox-backup?style=flat-square)](https://github.com/mikevansighem/dropbox-backup/issues)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/mikevansighem/dropbox-backup?style=flat-square)](https://github.com/mikevansighem/dropbox-backup/releases)

![Supports armhf Architecture](https://img.shields.io/badge/armhf-yes-green?style=flat-square)
![Supports armv7 Architecture](https://img.shields.io/badge/armv7-yes-green?style=flat-square)
![Supports aarch64 Architecture](https://img.shields.io/badge/aarch64-yes-green?style=flat-square)
![Supports amd64 Architecture](https://img.shields.io/badge/amd64-yes-green?style=flat-square)
![Supports i386 Architecture](https://img.shields.io/badge/i386-yes-green?style=flat-square)

Upload your Home Assistant backups to Dropbox.

## :page_facing_up: About

This add-on allows you to upload your Home Assistant backups to your Dropbox,
keeping your backups safe and available in case of hardware failure. Uploads
are triggered via a service call, making it easy to automate periodic backups
or trigger uploads to Dropbox via a script as you would with any other Home
Assistant service.

This add-on is inspired by [Dropbox Sync](https://github.com/danielwelch/hassio-dropbox-sync)
from [Daniel Welch](https://github.com/danielwelch). Major thanks for his work!

## 🏗 Dropbox Configuration

### Generate Dropbox access token

To access your personal Dropbox, this add-on requires an App (which has a key and a secret), and a long-lived refresh token. Dropbox access tokens live for a short period of time, whereas refresh tokens generated via the OAuth2 flow are permanent and do not expire - so we can use these for headless uploads.
Follow these steps to create the necessary items:

1. Go to [Your Dropbox apps](https://www.dropbox.com/developers/apps).
1. Click on `Create App`.
1. Select `Scoped Access` and choose between full or app folder only access.
1. Give your app a unique name and click on `Create App`.
1. Now your app is created go to the permissions tab and tick `files.metadata.write` and `files.content.write`.
1. Back on the settings tab, note the App Key and App Secret
1. Go to `https://www.dropbox.com/oauth2/authorize?client_id=<APP_KEY>&token_access_type=offline&response_type=code`
1. Authorise your App
1. It will display an Access code, note this
1. Using curl (or a tool like Postman/Reqbin if you prefer) create an OAuth2 Refresh Token
1. $ curl -X POST  https://api.dropboxapi.com/oauth2/token --user <APP_KEY>:<APP_SECRET> -H "Content-Type: application/x-www-form-urlencoded" -d 'code=<ACCESS_CODE>'
1. In the JSON output, look for the refresh_token and note it.

## ⤵️ Installation

1. Go to the Supervisor add-on store in Home Assistant.
1. Click on the "three-dots-menu" and choose `Repositories`.
1. Add this repository to your Home Assistant instance: `https://github.com/ianpleasance/dropbox-backup`.
1. Install the Dropbox backup add-on.
1. Configure the add-on with your Dropbox App Key, App Secret, OAuth2 Refresh Token and desired output directory (see configuration below).

## 🏗 Configuration

### Setup the add-on

Once you have created the token, copy it and the app key and secret into this add-on's configuration under
the `App key`, `App secret` and `Oauth refresh token` labels.

|Parameter|Required|Description|
|---------|--------|-----------|
|`app_key`|Yes|The "app" key for the app you generated above via the Dropbox UI.|
|`app_secret`|Yes|The "app" secret for the app you generated above via the Dropbox UI.|
|`oauth_refresh_token`|Yes|The "app" Oauth2 long lived refresh token you generated above via curl.|
|`output`|No|The target directory in Dropbox to which you want to upload. If left empty, defaults to `/`, which represents the top level of directory of your Dropbox.|
|`keep_last`|No|If set, the number of backups to keep locally. If there are more than this number of backups stored locally, the older backups will be deleted from local storage after being uploaded to Dropbox. If not set, no backups are deleted from local storage.|
|`preserve filename`|No|If set to `true` the backup filename will remain the original slug e.g. `d6f0919b.tar` otherwise the files will be renamed to the backup name e.g. `My Backup 2020-01-23.tar`. Some HASS Add-Ons create backups without a timestamp in the name, meaning that there could be more than one backup named "My Backup 2020-01-23.tar", Dropbox filenames must be unique and so to avoid conflict the addon will add the timestamp to the backup name. |
|`debug_info`|No|If set to `true` extra debugging info will be displayed.|

Example configuration:

```yaml
{
  app_key: "<APP_KEY>"
  app_secret: "<APP_SECRET>"
  oauth_refresh_token: "<YOUR_REFRESH_TOKEN>"
  output: "/hasssio-backups/"
  keep_last: 2
  preserve_filename: false
  debug_info: false
}
```

## 🚀 Usage

Dropbox Sync uploads all backup files (specifically, all `.tar` files) in the
Home Assistant `/backup` directory to a specified path in your Dropbox. This
target path is specified via the `output`option. Once the add-on is started, it
is listening for service calls.

After the add-on is configured and started, trigger an upload by calling the
`hassio.addon_stdin` service with the following service data:

```yaml
service: hassio.addon_stdin
data:
  addon: 782428ea_dropbox-backup
  input:
    command: upload

```

This triggers the `dropbox_uploader.sh` script with the provided access token.
You can use Home Assistant automations or scripts to run uploads at certain
time intervals, under certain conditions, etc.

A sample automation can be found [here](DOCS/sample_automation.md). To use it
simply create a new automation and copy the YAML.

## 📝 License

This add-on is covered under the MIT license refer to [LICENSE.md](LICENSE.md)
for details.
