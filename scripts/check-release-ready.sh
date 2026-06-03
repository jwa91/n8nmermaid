#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: scripts/check-release-ready.sh <release-tag>" >&2
  exit 2
fi

tag="$1"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
version="$(tr -d '[:space:]' < "${repo_root}/VERSION")"

if [ "$tag" != "v${version}" ]; then
  echo "Release tag ${tag} does not match VERSION ${version}; expected v${version}" >&2
  exit 1
fi

if ! git -C "$repo_root" diff --quiet || ! git -C "$repo_root" diff --cached --quiet; then
  echo "Working tree has uncommitted changes" >&2
  exit 1
fi

if ! git -C "$repo_root" verify-commit HEAD >/dev/null 2>&1; then
  echo "HEAD commit must be GPG-signed" >&2
  exit 1
fi

if [ "$(git -C "$repo_root" rev-parse "${tag}^{commit}")" != "$(git -C "$repo_root" rev-parse HEAD)" ]; then
  echo "${tag} must exist and point at HEAD" >&2
  exit 1
fi

if [ "$(git -C "$repo_root" cat-file -t "$tag")" != "tag" ]; then
  echo "${tag} must be an annotated signed tag, not a lightweight tag" >&2
  exit 1
fi

git -C "$repo_root" tag -v "$tag" >/dev/null

echo "${tag} git preflight passed"
