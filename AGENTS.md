# n8nmermaid API

This repo contains the Python/FastAPI backend for n8nMermaid.

## Deployment Model

- Production deploys are signed Forgejo semver releases from
  `jwa91/vps-n8nmermaid-api`.
- Build the Linux/amd64 Docker image before publishing a release. Release
  builds use the locked `uv.lock` dependency graph and package the prebuilt
  image archive in the release tarball.
- Edge does not run Git checkouts, source resets, or Docker builds for this
  API. It verifies release assets, loads `n8nmermaid-api:<tag>` with
  `docker load`, updates symlinks, and restarts the runtime Compose stack.
- `/var/services/n8nmermaid` is a compatibility symlink to
  `/opt/n8nmermaid-api/current` on edge.
- Runtime environment lives at `/etc/n8nmermaid-api/env`, not in release
  artifacts. Default runtime logging is `LOGGING_TARGET=CONSOLE` and
  `N8NMERMAID_LOG_LEVEL=INFO`.

## Release Workflow

1. Work on a branch, not directly on `main`.
2. Ensure the final release commit is GPG-signed.
3. Update `VERSION` and `compose.runtime.yaml` together.
4. Create a signed annotated tag that matches `VERSION`, for example:
   `git tag -s v0.3.0 -m "n8nmermaid-api v0.3.0"`.
5. Run `make release`.

`make release` intentionally fails early if the signed tag does not already
exist, does not point at `HEAD`, or if `HEAD` is not signed.

## Rules

- Keep the API contract unchanged unless explicitly requested:
  `/`, `/docs`, `/v2/mermaid`, and `/v2/report`.
- Do not add runtime secrets or live `.env` values to release artifacts.
- Do not reintroduce `docker compose up --build` for edge deploys.
