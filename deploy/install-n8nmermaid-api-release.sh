#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <release-dir>" >&2
  exit 2
fi

if [ "$(id -u)" -ne 0 ]; then
  echo "Must run as root" >&2
  exit 1
fi

release_dir="$(cd "$1" && pwd)"
current_symlink="${CURRENT_RELEASE_SYMLINK:-/opt/n8nmermaid-api/current}"
service_link="${SERVICE_LINK:-/var/services/n8nmermaid}"
env_file="${N8NMERMAID_API_ENV_FILE:-/etc/n8nmermaid-api/env}"
legacy_backup_parent="${N8NMERMAID_API_LEGACY_BACKUP_PARENT:-/var/services}"

for required in \
  "${release_dir}/VERSION" \
  "${release_dir}/compose.runtime.yaml" \
  "${release_dir}/manifest.json" \
  "${release_dir}/SHA256SUMS" \
  "${release_dir}/systemd/n8nmermaid-api-stack.service" \
  "${release_dir}/deploy/install-n8nmermaid-api-release.sh"
do
  if [ ! -e "$required" ]; then
    echo "Release is missing required path: $required" >&2
    exit 1
  fi
done

version="$(tr -d '[:space:]' < "${release_dir}/VERSION")"
tag="v${version}"
image_name="n8nmermaid-api:${tag}"
image_archive="${release_dir}/images/n8nmermaid-api-${tag}.tar"

if [ ! -e "$image_archive" ]; then
  echo "Release is missing required path: $image_archive" >&2
  exit 1
fi

if [ ! -x "${release_dir}/deploy/install-n8nmermaid-api-release.sh" ]; then
  echo "Release installer must be executable" >&2
  exit 1
fi

compose_image="$(awk '$1 == "image:" && $2 ~ /^n8nmermaid-api:v[0-9]+\.[0-9]+\.[0-9]+$/ {print $2; exit}' "${release_dir}/compose.runtime.yaml")"
if [ "$compose_image" != "$image_name" ]; then
  echo "Compose image ${compose_image:-<empty>} does not match release image ${image_name}" >&2
  exit 1
fi

(cd "$release_dir" && sha256sum -c SHA256SUMS)

install -d -o root -g root -m 0755 /opt/n8nmermaid-api "$(dirname "$service_link")" "$legacy_backup_parent"
install -d -o root -g root -m 0755 /etc/n8nmermaid-api

if [ ! -f "$env_file" ] && [ -f "${service_link}/.env" ]; then
  install -o root -g root -m 0600 "${service_link}/.env" "$env_file"
  echo "Migrated legacy ${service_link}/.env to ${env_file}"
fi

if [ ! -f "$env_file" ]; then
  default_env_tmp="$(mktemp)"
  {
    echo "LOGGING_TARGET=CONSOLE"
    echo "N8NMERMAID_LOG_LEVEL=INFO"
  } > "$default_env_tmp"
  install -o root -g root -m 0600 "$default_env_tmp" "$env_file"
  rm -f "$default_env_tmp"
  echo "Installed default ${env_file}"
fi

ln -sfn "$release_dir" "${current_symlink}.tmp"
mv -Tf "${current_symlink}.tmp" "$current_symlink"

if [ -L "$service_link" ]; then
  ln -sfn "$current_symlink" "${service_link}.tmp"
  mv -Tf "${service_link}.tmp" "$service_link"
elif [ -e "$service_link" ]; then
  if [ -d "$service_link" ] && [ -z "$(find "$service_link" -mindepth 1 -maxdepth 1 -print -quit)" ]; then
    rmdir "$service_link"
    ln -s "$current_symlink" "$service_link"
  elif [ -d "$service_link" ] && [ -d "${service_link}/.git" ]; then
    backup_path="${legacy_backup_parent}/n8nmermaid.git-backup.$(date -u +%Y%m%dT%H%M%SZ)"
    mv "$service_link" "$backup_path"
    ln -s "$current_symlink" "$service_link"
    echo "Moved legacy git worktree to ${backup_path}"
  else
    echo "${service_link} exists and is not an empty directory, symlink, or git worktree" >&2
    exit 1
  fi
else
  ln -s "$current_symlink" "$service_link"
fi

install -o root -g root -m 0644 "${release_dir}/systemd/n8nmermaid-api-stack.service" /etc/systemd/system/n8nmermaid-api-stack.service
systemctl daemon-reload

docker load -i "$image_archive"
docker image inspect "$image_name" >/dev/null

(
  cd "$release_dir"
  COMPOSE_PROJECT_NAME=n8nmermaid-api N8NMERMAID_API_ENV_FILE="$env_file" docker compose -f compose.runtime.yaml config --quiet
)

for container in n8nmermaid-api n8nmermaid-api-container; do
  if docker inspect "$container" >/dev/null 2>&1; then
    project="$(docker inspect "$container" --format '{{ index .Config.Labels "com.docker.compose.project" }}' 2>/dev/null || true)"
    if [ "$container" = "n8nmermaid-api-container" ] || [ "$project" != "n8nmermaid-api" ]; then
      echo "Removing legacy ${container} container from compose project ${project:-<none>}"
      docker rm -f "$container" >/dev/null
    fi
  fi
done

if systemctl is-active --quiet n8nmermaid-api-stack.service; then
  systemctl restart n8nmermaid-api-stack.service
else
  systemctl enable --now n8nmermaid-api-stack.service
fi

(
  cd "$release_dir"
  COMPOSE_PROJECT_NAME=n8nmermaid-api N8NMERMAID_API_ENV_FILE="$env_file" docker compose -f compose.runtime.yaml ps
)

for attempt in $(seq 1 30); do
  if curl -fsS http://localhost:8000/ >/dev/null 2>&1; then
    echo "n8nmermaid-api health check passed"
    echo "Installed n8nmermaid-api release from ${release_dir}"
    exit 0
  fi
  sleep 2
done

echo "n8nmermaid-api health check failed; check journalctl -u n8nmermaid-api-stack.service and docker logs n8nmermaid-api" >&2
exit 1
