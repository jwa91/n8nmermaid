#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Usage: $0 <release-tag> [gpg-key-id]" >&2
  exit 2
fi

tag="$1"
key_id="${2:-${RELEASE_SIGNING_KEY_ID:-CE95C51AC2ADB33C63D0DBBEAA2B33748BF3C5BA}}"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
release_artifacts_dir="${RELEASE_ARTIFACTS_DIR:-${repo_root}/release-artifacts}"
package_file="${release_artifacts_dir}/${tag}.tar.gz"
checksums_file="${release_artifacts_dir}/${tag}-checksums.txt"
public_key="${RELEASE_SIGNING_PUBLIC_KEY:-${repo_root}/keys/release-signing.asc}"
tmp_dir=""

cleanup() {
  if [ -n "$tmp_dir" ]; then
    rm -rf "$tmp_dir"
  fi
}
trap cleanup EXIT

for file in "$package_file" "$checksums_file" "$public_key"; do
  if [ ! -f "$file" ]; then
    echo "Missing file: ${file}" >&2
    exit 1
  fi
done

tmp_dir="$(mktemp -d)"
install -d -m 0700 "${tmp_dir}/gnupg"
GNUPGHOME="${tmp_dir}/gnupg" gpg --batch --quiet --import "$public_key"

for file in "$package_file" "$checksums_file"; do
  rm -f "${file}.sig"
  gpg --batch --yes --armor --local-user "$key_id" --output "${file}.sig" --detach-sign "$file"
  GNUPGHOME="${tmp_dir}/gnupg" gpg --batch --quiet --trust-model always --verify "${file}.sig" "$file"
  echo "Signed ${file}"
done
