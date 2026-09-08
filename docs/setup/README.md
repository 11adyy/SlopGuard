# SlopGuard setup

This guide covers the complete setup for the GitHub App, public webhook URL, network access, and deployment.

## 1. Create the GitHub App

Follow [GitHub App setup](github-app.md) to create the App with the exact permissions and webhook events SlopGuard needs.

## 2. Choose the public URL

Choose one of these deployment models:

- A hosted service that provides a public URL automatically.
- A server with a domain and HTTPS.
- A machine with a public IP and port forwarding.

Follow [Network setup](network.md) for the requirements of each model.

## 3. Configure the environment

Copy `.env.example` to `.env`, add the required GitHub and model credentials, and keep `IP_SYNC=true` unless you are configuring a fixed webhook URL manually.

## 4. Start SlopGuard

```bash
python main.py
```

When `IP_SYNC=true`, SlopGuard updates the GitHub App webhook URL during startup. Hosted deployments use the public URL exposed by the provider automatically; direct deployments fall back to public IP discovery.
