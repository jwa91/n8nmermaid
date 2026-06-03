#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <release-tag>" >&2
  exit 2
fi

tag="$1"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
release_artifacts_dir="${RELEASE_ARTIFACTS_DIR:-${repo_root}/release-artifacts}"
package_file="${release_artifacts_dir}/${tag}.tar.gz"
checksums_file="${release_artifacts_dir}/${tag}-checksums.txt"
forgejo_host="${FORGEJO_HOST:-forgejo.janwillemaltink.com}"
forgejo_repo="${FORGEJO_REPO:-jwa91/vps-n8nmermaid-api}"
version="$(tr -d '[:space:]' < "${repo_root}/VERSION")"
image_name="${N8NMERMAID_API_IMAGE:-n8nmermaid-api:${tag}}"

if [ "$tag" != "v${version}" ]; then
  echo "Release tag ${tag} does not match VERSION ${version}; expected v${version}" >&2
  exit 1
fi

if [ "$(git -C "$repo_root" rev-parse "${tag}^{commit}")" != "$(git -C "$repo_root" rev-parse HEAD)" ]; then
  echo "${tag} must exist and point at HEAD before publishing" >&2
  exit 1
fi

if ! git -C "$repo_root" verify-commit HEAD >/dev/null 2>&1; then
  echo "HEAD commit must be GPG-signed before publishing" >&2
  exit 1
fi

if ! git -C "$repo_root" verify-tag "$tag" >/dev/null 2>&1; then
  echo "${tag} must be an annotated GPG-signed tag before publishing" >&2
  exit 1
fi

for file in "$package_file" "$checksums_file" "${package_file}.sig" "${checksums_file}.sig"; do
  if [ ! -f "$file" ]; then
    echo "Missing release asset: ${file}" >&2
    exit 1
  fi
done

body="n8nmermaid API ${version}

FastAPI backend release with prebuilt runtime image.

Build:
- Runtime image: ${image_name}
- Platform: linux/amd64
- Dependencies: uv.lock with uv sync --frozen --no-dev

Assets:
- ${tag}.tar.gz
- checksums.txt
- ${tag}.tar.gz.sig
- checksums.txt.sig

Edge deploy must verify the checksum and GPG signatures, load the image archive, and health-check http://127.0.0.1:8000/."

fj -H "$forgejo_host" release create "$tag" \
  -r "$forgejo_repo" \
  -t "$tag" \
  -b "$body" \
  --attach "${package_file}:$(basename "$package_file")" \
  --attach "${checksums_file}:checksums.txt" \
  --attach "${package_file}.sig:$(basename "$package_file").sig" \
  --attach "${checksums_file}.sig:checksums.txt.sig"
