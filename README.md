# SlopGuard
[![Stars](https://img.shields.io/github/stars/11adyy/SlopGuard)](https://github.com/11adyy/SlopGuard/stargazers)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![License](https://img.shields.io/github/license/11adyy/SlopGuard)
![GitHub App](https://img.shields.io/badge/GitHub-App-black?logo=github)

SlopGuard is a GitHub App webhook service that checks issue and pull request text for signals commonly associated with AI-generated writing.

It analyzes issue titles and bodies, plus pull request titles and descriptions. Pull request diffs and GitHub Discussions are planned for future releases.

## How it works

1. GitHub sends an `issues` or `pull_request` webhook to `/webhooks`.
2. SlopGuard verifies the GitHub signature before reading the payload.
3. Edits pass through a deterministic change gate. Title edits are analyzed immediately; body edits are analyzed when the normalized change reaches `REANALYSIS_CHANGE_THRESHOLD`.
4. A controlled LangGraph runs the explicit Python pattern detector and the AI-writing review prompt.
5. An OpenAI-compatible model returns a typed probability, reasons, and caveat.
6. SlopGuard applies `AI_DETECTION_THRESHOLD` itself to derive the final verdict.
7. SlopGuard updates one bot comment and applies the configured GitHub action.

The webhook route and the full processing pipeline are asynchronous. GitHub API calls and model calls use async clients, while local pattern analysis runs off the event loop.

## Project structure

```text
src/slopguard/
  api/
    app.py                FastAPI application and the single webhook route
  core/
    lifespan.py           Application startup and shutdown
    logging.py            Logging configuration
    security.py           GitHub webhook signature verification
    settings.py           Typed environment configuration
  modules/
    detection/            LangGraph workflow and Python detection nodes
    github/               GitHub App authentication and REST operations
    webhooks/              Payload models, edit routing, and orchestration
  prompts/
    detection.py          Explicit detection and comment prompts
main.py                   Uvicorn entrypoint
```

## Set up

The complete step-by-step setup guide is available in [`docs/setup/`](docs/setup/README.md).

Please feel free to contact github@11adyy.dev in case you don't understand something, I'd love to help you :)

### 1. Installation

Requirements:

- Python 3.12 or newer
- A GitHub App installed on the repositories to monitor
- An OpenAI-compatible chat model

Install the project and development tools:

```bash
python -m pip install -e ".[dev]"
```

### 2. GitHub App

Create a GitHub App with:

- Issues: read and write
- Pull requests: read and write
- Repository metadata: read-only

Subscribe the App to these webhook events:

- Issues
- Pull request

Enable the webhook and set a strong, non-empty secret. Copy that exact secret to
`GITHUB_WEBHOOK_SECRET`; SlopGuard refuses to start without it and verifies every
delivery with `X-Hub-Signature-256`.

The user-authorization, refresh-token, and device-flow options are not required.
SlopGuard authenticates as the App: it creates a fresh short-lived JWT for each
GitHub request and a fresh installation access token when repository access is
needed, so expired App tokens are renewed automatically without storing user
tokens.

### 3. Environment Setup

Copy `.env.example` to `.env`.

Required variables:

| Variable | Purpose |
| --- | --- |
| `GITHUB_APP_ID` | GitHub App identifier |
| `GITHUB_PRIVATE_KEY` | GitHub App private key |
| `GITHUB_WEBHOOK_SECRET` | Webhook signature secret |
| `LLM_API_KEY` | OpenAI-compatible API key |

#### !! If you are NOT using OpenAI, remember to change `LLM_BASE_URL` and `LLM_MODEL` to match your OpenAI-compatible provider API.

Defaulted variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `LLM_BASE_URL` | `https://api.openai.com/v1` | OpenAI-compatible API base URL |
| `LLM_MODEL` | `gpt-4o-mini` | Detection model |
| `LLM_MAX_TOKENS` | `1024` | Maximum output tokens reserved for one assessment |
| `SERVER_HOST` | `0.0.0.0` | Local bind address |
| `SERVER_PORT` | `8000` | Local Uvicorn port |
| `PUBLIC_WEBHOOK_SCHEME` | `http` | Public webhook URL scheme |
| `PUBLIC_WEBHOOK_PORT` | `8000` | Port GitHub can reach |
| `PUBLIC_IP_DISCOVERY_URL` | `https://api.ipify.org` | Public IP discovery endpoint |
| `IP_SYNC` | `true` | Update the GitHub App URL from the hosting URL or public IP on startup |
| `AI_DETECTION_THRESHOLD` | `0.50` | Minimum probability for `ai-written` |
| `REANALYSIS_CHANGE_THRESHOLD` | `0.50` | Minimum normalized body change for edited events |
| `AI_DETECTED_ACTION` | `tag` | Default action for AI-written content |
| `NO_AI_DETECTED_ACTION` | `tag` | Default action for human-written content |
| `AI_WRITTEN_LABEL` | `ai-written` | AI verdict label |
| `HUMAN_WRITTEN_LABEL` | `human-written` | Human verdict label |

#### !! If you are using your own domain configured in GitHub, set `IP_SYNC=false`.

When `IP_SYNC=true`, SlopGuard uses the public URL supplied by a **supported** hosting provider. If no provider URL is available, configure your PHYSICAL router to forward `PUBLIC_WEBHOOK_PORT` to `SERVER_PORT`, allow that port through the PC FIREWALL, and SlopGuard will discover the public IP and update GitHub to `http://PUBLIC_IP:PUBLIC_WEBHOOK_PORT/webhooks` on startup.

Optional subject-specific action overrides:

| Variable | Overrides |
| --- | --- |
| `AI_DETECTED_ISSUE_ACTION` | `AI_DETECTED_ACTION` for issues |
| `AI_DETECTED_PULL_REQUEST_ACTION` | `AI_DETECTED_ACTION` for pull requests |
| `NO_AI_DETECTED_ISSUE_ACTION` | `NO_AI_DETECTED_ACTION` for issues |
| `NO_AI_DETECTED_PULL_REQUEST_ACTION` | `NO_AI_DETECTED_ACTION` for pull requests |

Actions work as follows:

- `tag`: add the matching verdict label and remove the opposite verdict label.
- `comment`: update the SlopGuard result comment without changing labels or state.
- `close`: update the result comment and close the issue or pull request. This is available for AI-detected actions.
- `nothing`: update the result comment without adding labels or closing the item. This is available for non-AI actions.

Every completed analysis updates one result comment. The configured action controls the additional GitHub mutation.

## Run

Start the service with:

```bash
python main.py
```

The service listens on `http://0.0.0.0:8000`.

## Detection design

Detection is implemented as explicit Python nodes and prompts for full control:

- Unicode normalization catches invisible characters and common lookalike substitutions.
- Pattern matching checks high-signal vocabulary, formulaic phrases, chatbot artifacts, markup leaks, promotional language, and structural formatting.
- The LangGraph model review combines those findings with the submitted text and requires a typed response.
- Short text receives a lower-confidence treatment unless several independent signals or a definitive artifact are present.


## Roadmap

1. Current: asynchronous GitHub App webhook processing for issue and pull request text, deterministic pattern detection, LangGraph adjudication, comments, labels, and configurable actions.
2. Diff checking: analyze pull request changes and distinguish AI-written descriptions from AI-generated code or patch content.
3. Discussions: extend webhook coverage and AI-writing checks to GitHub Discussions.
4. Review intelligence: add repository-level policies, configurable detection profiles, historical verdicts, and maintainer review feedback.

## Development

```bash
python -m pytest -q
python -m ruff check .
python -m mypy src/slopguard main.py
```
