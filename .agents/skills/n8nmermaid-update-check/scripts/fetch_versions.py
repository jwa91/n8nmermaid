#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests"]
# ///
"""
Fetch current and latest versions for n8nmermaid service dependencies.
Checks Python runtime and package updates via uv.

Usage: uv run fetch_versions.py [repo_root]
"""

import json
import re
import subprocess
import sys
from pathlib import Path

import requests


def get_dockerfile_python_version(dockerfile_path: Path) -> str | None:
    """Extract Python version from Dockerfile."""
    content = dockerfile_path.read_text()

    # Match patterns like: FROM python:3.13-slim or FROM python:3.13
    match = re.search(r'FROM python:([\d.]+)', content)
    if match:
        return match.group(1)
    return None


def fetch_python_versions() -> dict:
    """Fetch Python versions from Docker Hub."""
    try:
        resp = requests.get(
            'https://hub.docker.com/v2/repositories/library/python/tags',
            params={'page_size': 100, 'name': 'slim'},
            timeout=10
        )

        if resp.status_code == 200:
            data = resp.json()
            tags = data.get('results', [])

            # Find version tags (X.Y-slim pattern)
            versions = []
            for tag in tags:
                name = tag.get('name', '')
                match = re.match(r'^(\d+\.\d+)-slim$', name)
                if match:
                    version = match.group(1)
                    versions.append({
                        'version': version,
                        'tag': name,
                        'last_updated': tag.get('last_updated')
                    })

            versions.sort(
                key=lambda x: [int(p) for p in x['version'].split('.')],
                reverse=True
            )

            return {
                'versions': versions[:10],
                'latest': versions[0]['version'] if versions else None
            }
    except Exception as e:
        return {'error': str(e)}

    return {'versions': [], 'latest': None}


def run_uv_outdated(repo_root: Path) -> dict:
    """Run uv tree --outdated to check for package updates."""
    result = subprocess.run(
        ['uv', 'tree', '--outdated'],
        cwd=repo_root,
        capture_output=True,
        text=True
    )

    packages = {'patch': [], 'minor': [], 'major': []}

    # Parse output like: ├── fastapi v0.115.12 (latest: v0.128.0)
    # Also handles: ├── ruff v0.11.7 (extra: dev) (latest: v0.14.14)
    pattern = re.compile(r'([a-zA-Z0-9_-]+)\s+v([\d.]+)(?:\s+\([^)]+\))?\s+\(latest:\s+v([\d.]+)\)')

    for line in result.stdout.split('\n'):
        match = pattern.search(line)
        if match:
            pkg_name = match.group(1)
            current = match.group(2)
            latest = match.group(3)

            # Categorize by version change
            try:
                curr_parts = current.split('.')
                lat_parts = latest.split('.')

                if curr_parts[0] != lat_parts[0]:
                    category = 'major'
                elif len(curr_parts) > 1 and len(lat_parts) > 1 and curr_parts[1] != lat_parts[1]:
                    category = 'minor'
                else:
                    category = 'patch'

                packages[category].append({
                    'name': pkg_name,
                    'current': current,
                    'latest': latest
                })
            except (IndexError, ValueError):
                packages['patch'].append({
                    'name': pkg_name,
                    'current': current,
                    'latest': latest
                })

    total = sum(len(v) for v in packages.values())
    return {
        'total': total,
        'categorized': packages,
        'raw_output': result.stdout
    }


def main():
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent.parent.parent

    if len(sys.argv) > 1:
        repo_root = Path(sys.argv[1])

    dockerfile_path = repo_root / 'Dockerfile'
    pyproject_path = repo_root / 'pyproject.toml'

    if not dockerfile_path.exists():
        print(json.dumps({'error': f'Dockerfile not found at {dockerfile_path}'}))
        sys.exit(1)

    if not pyproject_path.exists():
        print(json.dumps({'error': f'pyproject.toml not found at {pyproject_path}'}))
        sys.exit(1)

    # Get current Python version from Dockerfile
    current_python = get_dockerfile_python_version(dockerfile_path)

    # Fetch Python versions
    python_info = fetch_python_versions()

    # Determine Python update status
    python_update = {'available': False, 'current': current_python}
    if current_python and python_info.get('latest'):
        current_parts = [int(p) for p in current_python.split('.')]
        latest_parts = [int(p) for p in python_info['latest'].split('.')]
        if latest_parts > current_parts:
            python_update['available'] = True
            python_update['latest'] = python_info['latest']

    # Check packages via uv
    packages_info = run_uv_outdated(repo_root)

    output = {
        'repo_root': str(repo_root),
        'python': {
            'current': current_python,
            'versions': python_info,
            'update': python_update
        },
        'packages': packages_info,
        'summary': {
            'python_update_available': python_update.get('available', False),
            'package_updates_available': packages_info.get('total', 0) > 0,
            'major_package_updates': len(packages_info.get('categorized', {}).get('major', [])),
            'minor_package_updates': len(packages_info.get('categorized', {}).get('minor', [])),
            'patch_package_updates': len(packages_info.get('categorized', {}).get('patch', []))
        }
    }

    print(json.dumps(output, indent=2, default=str))


if __name__ == '__main__':
    main()
