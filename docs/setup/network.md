# Network setup

GitHub must be able to reach `POST /webhooks` from the public Internet. `localhost`, `127.0.0.1`, and a private LAN address are not valid webhook destinations.

## Hosted deployment with an automatic public URL

When the hosting provider exposes its public URL through the runtime environment, SlopGuard detects it automatically. Keep:

```env
IP_SYNC=true
```

The detected URL is used as:

```text
https://provider-domain.example/webhooks
```

The current automatic URL detection covers Render, Railway, Heroku, Fly.io, Vercel, Replit, Koyeb, Northflank, Zeabur, Dokku, and Cloud Run-compatible URL variables.

For Render, the public URL is the service's `onrender.com` address. Render terminates HTTPS at its edge and forwards the request to the service, so do not use the outbound IP returned by an IP discovery service as the webhook URL.

The process must listen on `0.0.0.0`. Hosted providers can inject `PORT`; SlopGuard uses that value when it is available and otherwise uses `SERVER_PORT`.

## Deployment with a domain

If you already have a domain with HTTPS:

1. Point the domain or subdomain to the server or hosting service.
2. Configure TLS for the domain.
3. Set the GitHub App webhook URL to `https://your-domain.example/webhooks`.
4. Set `IP_SYNC=false` so SlopGuard does not replace the fixed domain during startup.

## Deployment with a public IP

If the server is running directly on a machine with a public IP:

1. Keep `IP_SYNC=true`.
2. Set `SERVER_HOST=0.0.0.0`.
3. Forward `PUBLIC_WEBHOOK_PORT` on the router to the machine's local IP and `SERVER_PORT`.
4. Allow the forwarded TCP port through the machine firewall.
5. SlopGuard discovers the public IP and updates the GitHub App URL to `http://PUBLIC_IP:PUBLIC_WEBHOOK_PORT/webhooks`.

HTTP is supported for direct IP deployments, but it does not encrypt traffic. The webhook signature protects authenticity and integrity; HTTPS is still recommended whenever it is available.

## Mobile tethering and CGNAT

USB tethering and mobile hotspots usually do not provide a router where you can create a port-forwarding rule. Mobile providers commonly place customers behind CGNAT, which prevents GitHub from opening an incoming connection to the device.

In that situation, use a hosted public URL or a server with a domain instead of direct IP synchronization.
