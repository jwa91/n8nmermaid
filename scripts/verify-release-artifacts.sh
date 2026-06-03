#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Usage: $0 <release-tag> [gpg-public-key]" >&2
  exit 2
fi

tag="$1"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
release_artifacts_dir="${RELEASE_ARTIFACTS_DIR:-${repo_root}/release-artifacts}"
package_file="${release_artifacts_dir}/${tag}.tar.gz"
checksums_file="${release_artifacts_dir}/${tag}-checksums.txt"
public_key="${2:-${RELEASE_SIGNING_PUBLIC_KEY:-${repo_root}/keys/release-signing.asc}}"
tmp_dir=""

cleanup() {
  if [ -n "$tmp_dir" ]; then
    rm -rf "$tmp_dir"
  fi
}
trap cleanup EXIT

for file in "$package_file" "$checksums_file" "${package_file}.sig" "${checksums_file}.sig" "$public_key"; do
  if [ ! -f "$file" ]; then
    echo "Missing file: ${file}" >&2
    exit 1
  fi
done

(cd "$release_artifacts_dir" && shasum -a 256 -c "$(basename "$checksums_file")")

tmp_dir="$(mktemp -d)"
install -d -m 0700 "${tmp_dir}/gnupg"
GNUPGHOME="${tmp_dir}/gnupg" gpg --batch --quiet --import "$public_key"
GNUPGHOME="${tmp_dir}/gnupg" gpg --batch --quiet --trust-model always --verify "${package_file}.sig" "$package_file"
GNUPGHOME="${tmp_dir}/gnupg" gpg --batch --quiet --trust-model always --verify "${checksums_file}.sig" "$checksums_file"

echo "Verified ${package_file}"
echo "Verified ${checksums_file}"
