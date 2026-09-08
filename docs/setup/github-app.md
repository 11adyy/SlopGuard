# GitHub App setup

Create the App from GitHub:

1. Open `GitHub → Settings → Developer settings → GitHub Apps`.
2. Select **New GitHub App**.
3. Enter `SlopGuard` as the App name, or another available name.
4. Set **Homepage URL** to `https://11adyy.dev`. This is the project website and documentation address.
5. Leave **Callback URL** empty.
6. Leave **Setup URL** empty.
7. Leave **Request user authorization during installation** disabled.
8. Leave **Enable Device Flow** disabled.

## Webhook settings

Enable the webhook and use these values:

- **Webhook URL:** `https://example.com/webhooks` while creating the App if you do not have a public URL yet. SlopGuard replaces this URL automatically during startup when `IP_SYNC=true`.
- **Secret:** generate a strong secret and copy the same value to `GITHUB_WEBHOOK_SECRET`.
- **SSL verification:** keep it enabled for HTTPS domains and hosted services. For a direct HTTP IP deployment, GitHub cannot verify a TLS certificate, so SSL verification must be disabled for that App webhook.

The webhook secret is mandatory. SlopGuard refuses to start without a non-empty `GITHUB_WEBHOOK_SECRET` and verifies every request with `X-Hub-Signature-256`.

## Repository permissions

Under **Permissions & events → Repository permissions**, select:

- **Issues:** Read and write
- **Pull requests:** Read and write
- **Metadata:** Read-only

Leave every other repository permission at **No access** unless a future SlopGuard feature explicitly requires it.

## Subscribe to events

Subscribe only to:

- **Issues**
- **Pull request**

Do not enable issue comments, pull request reviews, review comments, review threads, or Discussions yet. Discussions will be added in a future release.

## Private key and App ID

1. Save the **App ID** shown in the App settings as `GITHUB_APP_ID`.
2. In **Private keys**, select **Generate a private key**.
3. Store the downloaded `.pem` file securely.
4. Put its PEM contents in `GITHUB_PRIVATE_KEY`.

The Client ID and Client Secret are OAuth credentials and are not used by SlopGuard. The private key is the value required to create GitHub App JWTs.

## Install the App

Install the App on each repository that SlopGuard should monitor. Select the repositories explicitly when possible, then confirm that the App has access to Issues, Pull requests, and repository metadata.
