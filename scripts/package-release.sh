#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <release-tag>" >&2
  exit 2
fi

tag="$1"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
release_artifacts_dir="${RELEASE_ARTIFACTS_DIR:-${repo_root}/release-artifacts}"
package_dir="${release_artifacts_dir}/${tag}"
package_file="${release_artifacts_dir}/${tag}.tar.gz"
checksums_file="${release_artifacts_dir}/${tag}-checksums.txt"
repo_version="$(tr -d '[:space:]' < "${repo_root}/VERSION")"
git_commit="$(git -C "$repo_root" rev-parse HEAD)"
docker_bin="${DOCKER_BIN:-docker}"
image_name="${N8NMERMAID_API_IMAGE:-n8nmermaid-api:${tag}}"
platform="${N8NMERMAID_API_PLATFORM:-linux/amd64}"
compose_image="$(awk '$1 == "image:" && $2 ~ /^n8nmermaid-api:v[0-9]+\.[0-9]+\.[0-9]+$/ {print $2; exit}' "${repo_root}/compose.runtime.yaml")"
image_archive_name="n8nmermaid-api-${tag}.tar"
image_archive_path="${package_dir}/images/${image_archive_name}"
export COPYFILE_DISABLE=1

if [ "$tag" != "v${repo_version}" ]; then
  echo "Release tag ${tag} does not match VERSION ${repo_version}; expected v${repo_version}" >&2
  exit 1
fi

if [ -z "$compose_image" ]; then
  echo "compose.runtime.yaml must contain image: n8nmermaid-api:${tag}" >&2
  exit 1
fi

if [ "$compose_image" != "$image_name" ]; then
  echo "Compose image ${compose_image} does not match release image ${image_name}" >&2
  exit 1
fi

if [ "$platform" != "linux/amd64" ]; then
  echo "Release platform must be linux/amd64, got ${platform}" >&2
  exit 1
fi

if ! command -v "$docker_bin" >/dev/null 2>&1; then
  echo "Docker command not found: ${docker_bin}" >&2
  exit 1
fi

rm -rf "$package_dir"
rm -f "$package_file" "$checksums_file" "${package_file}.sig" "${checksums_file}.sig"
mkdir -p "${package_dir}/deploy" "${package_dir}/images" "${package_dir}/systemd"

(
  cd "$repo_root"
  "$docker_bin" build --platform "$platform" -t "$image_name" -f Dockerfile .
)

image_platform="$("$docker_bin" image inspect "$image_name" --format '{{.Os}}/{{.Architecture}}')"
if [ "$image_platform" != "$platform" ]; then
  echo "Built image ${image_name} has platform ${image_platform}; expected ${platform}" >&2
  exit 1
fi

"$docker_bin" save -o "$image_archive_path" "$image_name"

cp "${repo_root}/compose.runtime.yaml" "${package_dir}/compose.runtime.yaml"
cp "${repo_root}/VERSION" "${package_dir}/VERSION"
install -m 0755 "${repo_root}/deploy/install-n8nmermaid-api-release.sh" "${package_dir}/deploy/install-n8nmermaid-api-release.sh"
cp "${repo_root}/systemd/n8nmermaid-api-stack.service" "${package_dir}/systemd/n8nmermaid-api-stack.service"

image_id="$("$docker_bin" image inspect "$image_name" --format '{{.Id}}')"
image_digest="$(shasum -a 256 "$image_archive_path" | awk '{print $1}')"

cat >"${package_dir}/manifest.json" <<EOF
{
  "artifact_schema_version": 1,
  "tag": "${tag}",
  "repo_version": "${repo_version}",
  "git_commit": "${git_commit}",
  "docker_platform": "${platform}",
  "image": "${image_name}",
  "image_id": "${image_id}",
  "image_archive": "images/${image_archive_name}",
  "image_archive_sha256": "${image_digest}",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

(cd "$package_dir" && find . -type f ! -name SHA256SUMS -print | LC_ALL=C sort | sed 's|^\./||' | xargs shasum -a 256 > SHA256SUMS)
(cd "$release_artifacts_dir" && tar --no-xattrs -czf "$package_file" "$tag")
if tar -tzf "$package_file" | grep -E '(^|/)(\.DS_Store|\._[^/]+)$'; then
  echo "Release archive contains macOS metadata files" >&2
  exit 1
fi
(cd "$release_artifacts_dir" && shasum -a 256 "$(basename "$package_file")" > "$(basename "$checksums_file")")

echo "Packaged ${package_file}"
echo "Wrote ${checksums_file}"
