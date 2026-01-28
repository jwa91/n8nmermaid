---
name: n8nmermaid-update-check
description: Check for Python runtime and package updates in n8nmermaid. Handles FastAPI/Uvicorn updates and creates update PRs. Use when user asks to check for updates or upgrade dependencies.
---

# n8nmermaid Update Check

Check for Python runtime and package updates in the FastAPI n8nmermaid service.

## Workflow

1. Run version check script
2. Analyze results by category
3. Decide update strategy
4. Apply updates and create PR (or report blockers)

## Step 1: Check Versions

```bash
uv run .agents/skills/s-n8nmermaid-update-check/n8nmermaid-update-check/scripts/fetch_versions.py .
```

Output includes:
- Python: current version, latest available
- Packages: categorized as patch/minor/major updates (via `uv tree --outdated`)

## Step 2: Analyze Results

### Python Updates

**Same minor (patch):** e.g., 3.13.0 → 3.13.1
- Safe to update, just change Dockerfile tag

**New minor version:** e.g., 3.13 → 3.14
- Check Python release notes for deprecations
- Verify package compatibility (especially native extensions)
- Test build locally before updating

### Package Updates

**Patch updates:** Auto-update safe
**Minor updates:** Usually safe, quick changelog review
**Major updates:** Review changelogs carefully, especially:

- `fastapi` - Web framework, check migration guides
- `uvicorn` - ASGI server, usually backward compatible
- `pydantic` - Data validation, v2 had significant changes
- `typer` - CLI framework
- `ruff` - Linter, may add new rules

### FastAPI + Starlette + Pydantic

These packages are tightly coupled. When updating FastAPI:
- Check compatible Starlette version
- Check compatible Pydantic version
- FastAPI release notes usually specify compatible versions

## Step 3: Decision Tree

```
No updates available?
  → Report "All up to date" and stop

Only patch updates?
  → Auto-update: uv lock --upgrade, test, create PR

Minor updates present?
  → Update all, test build and API
  → If issues: revert problematic packages, report

Major updates present?
  → Fetch changelogs for major packages
  → Check for breaking changes
  → Safe: include in update
  → Breaking: report to user with migration notes

Python update available?
  → Check package compatibility
  → Test locally before updating Dockerfile
```

## Step 4a: Apply Updates

```bash
# Create branch
git checkout -b update/deps-$(date +%Y%m%d)

# Update all packages
uv lock --upgrade

# For specific package updates:
uv add fastapi@latest uvicorn@latest

# For Python update, edit Dockerfile:
# Change: FROM python:3.13-slim → FROM python:3.14-slim

# Sync dependencies
uv sync

# Test the API
uv run uvicorn src.n8nmermaid.api.main:app --host 0.0.0.0 --port 8000

# Run linting
uv run ruff check .

# If everything passes, commit
git add -A
git commit -m "Update dependencies

Python: [version change if applicable]
Major: [list major updates]
Minor: [count] packages
Patch: [count] packages"

# Push and create PR
git push -u origin update/deps-$(date +%Y%m%d)
gh pr create --title "Update dependencies" --body "..."
```

## Step 4b: Report Blockers

If updates are blocked, report to user:
1. What major updates have breaking changes
2. Specific migration steps needed
3. Recommended order of updates

## FastAPI Special Handling

Check for breaking changes before updating:

```bash
# Check FastAPI releases
gh api repos/tiangolo/fastapi/releases --jq '.[0:5] | .[].body' | head -100
```

Common breaking patterns:
- Dependency injection changes
- Request/Response model changes
- OpenAPI schema changes
- Middleware API changes

After FastAPI updates, verify:
- API starts: `uv run uvicorn src.n8nmermaid.api.main:app`
- Endpoints respond correctly
- OpenAPI docs generate (`/docs`)

## Pydantic v2 Notes

If still on Pydantic v1, migration to v2 requires:
- Model syntax changes (`.dict()` → `.model_dump()`)
- Validator decorator changes
- Config class changes

This project uses Pydantic v2, so minor updates should be safe.

## Testing

After any updates, verify:
```bash
uv sync                    # Sync dependencies
uv run ruff check .        # Linting
uv run uvicorn src.n8nmermaid.api.main:app  # Start API
# Test endpoints manually or with curl
```
