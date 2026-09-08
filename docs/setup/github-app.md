# GitHub App setup

Create the App from GitHub:

1. Open `GitHub → Settings → Developer settings → GitHub Apps`.
2. Select **New GitHub App**.
3. Enter `SlopGuard` as the App name, or another available name.
4. Set **Homepage URL** to `https://11adyy.dev`. This is the project creator's website, just to support him, leave blank if you don't want to.
5. Leave **Callback URL** empty.
6. Leave **Setup URL** empty.
7. Leave **Request user authorization during installation** disabled.
8. Leave **Enable Device Flow** disabled.

## Webhook settings

Enable the webhook and use these values:

- **Webhook URL:** `https://example.com/webhooks` while creating the App if you DO NOT have a domain to deploy this (which you don't have probably so just do example.com). SlopGuard replaces this URL automatically at startup because IPs change a lot, when `IP_SYNC=true`, if you hace a domain set IP_SYNC=False.
- **Secret:** generate a strong secret and copy the same value to `GITHUB_WEBHOOK_SECRET`.
- **SSL verification:** Disable it if you don't have a domain. If your repository contains sensitive information that requires strong privacy, consider getting a domain.

The webhook secret is mandatory. Just put your super hiper secret password there, make sure nobody discovers it 👀.

## Repository permissions

Under **Permissions & events → Repository permissions**, select:

- **Issues:** Read and write
- **Pull requests:** Read and write
- **Metadata:** Read-only (Automatic)

Leave every other repository permission at **No access** unless a future SlopGuard feature explicitly requires it, you can change this later in the app settings.

## Subscribe to events

Subscribe only to:

- **Issues**
- **Pull request**

Do not enable issue comments, pull request reviews, review comments, review threads, or Discussions yet. Discussions will be added in a future release.

## Private key and App ID

1. Save the **App ID** shown in the App settings as `GITHUB_APP_ID`.
2. In **Private keys**, select **Generate a private key**.
3. Store the downloaded `.pem` file securely.
4. Copy and paste the file's contents in `GITHUB_PRIVATE_KEY` env.

The Client ID and Client Secret are OAuth credentials and are not used by SlopGuard. The private key is the value required to create GitHub App JWTs.

## Install the App

Install the App on each repository that SlopGuard should monitor. Select the repositories explicitly when possible, then confirm that the App has access to Issues, Pull requests, and repository metadata.
