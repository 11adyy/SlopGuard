# Changelog

All notable changes to SlopGuard will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-08

### Added

- **GitHub App webhook service** for detecting AI-generated content in issues and pull requests
- **Webhook signature verification** using GitHub's `X-Hub-Signature-256` header for secure payload validation
- **Deterministic change gate** for edit events (title edits analyzed immediately, body edits analyzed only when change exceeds threshold)
- **Pattern detection** using explicit Python nodes:
  - Unicode normalization to catch invisible characters and lookalike substitutions
  - High-signal vocabulary and formulaic phrase detection
  - Chatbot artifact identification
  - Markup leak detection
  - Promotional language and structural formatting checks
- **LangGraph workflow** for AI-writing detection with typed responses (probability, reasons, caveats)
- **OpenAI-compatible model integration** for flexible LLM provider support
- **Configurable actions** on AI detection:
  - `tag`: Add/remove verdict labels
  - `comment`: Update result comment
  - `close`: Close issues/pull requests
  - `nothing`: Update comment without additional mutations
- **Subject-specific action overrides** for issues vs. pull requests
- **Asynchronous processing** for webhooks and GitHub API calls
- **FastAPI application** with single webhook route (`/webhooks`)
- **Uvicorn entrypoint** with configurable host and port
- **Comprehensive environment configuration** via typed `settings.py`
- **GitHub App authentication** with automatic JWT and installation token generation (no token storage)
- **Logging configuration** for debugging and monitoring
- **Development tools**:
  - pytest for testing
  - ruff for linting
  - mypy for type checking
- **Documentation**:
  - Setup guide with GitHub App configuration
  - Network setup guidance for various deployment models
  - Environment variable reference and best practices
  - Project structure overview
  - Detection design documentation

### Security

- GitHub webhook signature verification on every delivery
- No storage of user tokens or refresh tokens
- Fresh JWT and installation tokens generated per request
- Private key handling guidelines in documentation
- Security policy for vulnerability reporting

### Known Limitations

- Pull request diffs not yet analyzed (planned for future release)
- GitHub Discussions not yet supported (planned for future release)
- Repository-level policies and detection profiles not yet implemented (planned)
- Historical verdict tracking not yet available (planned)

## [Unreleased]

### Planned Features

- Diff checking for pull request changes (distinguish AI-written descriptions from AI-generated code)
- GitHub Discussions support with webhook coverage
- Review intelligence with repository-level policies and configurable detection profiles
- Historical verdict tracking and maintainer review feedback

---

For upgrade instructions and migration guides, see [CONTRIBUTING.md](CONTRIBUTING.md).
