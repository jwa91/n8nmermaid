VERSION ?= $(shell tr -d '[:space:]' < VERSION)
TAG ?= v$(VERSION)

export RELEASE_SIGNING_KEY_ID ?= CE95C51AC2ADB33C63D0DBBEAA2B33748BF3C5BA
export RELEASE_SIGNING_PUBLIC_KEY ?= $(CURDIR)/keys/release-signing.asc
export N8NMERMAID_API_IMAGE ?= n8nmermaid-api:$(TAG)
export N8NMERMAID_API_PLATFORM ?= linux/amd64

.PHONY: check check-release-ready package sign verify push-release publish release clean

check:
	N8NMERMAID_API_ENV_FILE=.env.example docker compose -f compose.runtime.yaml config --quiet
	bash -n scripts/*.sh deploy/*.sh
	if command -v systemd-analyze >/dev/null 2>&1; then systemd-analyze verify systemd/n8nmermaid-api-stack.service; fi

check-release-ready:
	scripts/check-release-ready.sh "$(TAG)"

package: check
	scripts/package-release.sh "$(TAG)"

sign:
	scripts/sign-release-artifacts.sh "$(TAG)"

verify:
	scripts/verify-release-artifacts.sh "$(TAG)"

push-release:
	scripts/check-release-ready.sh "$(TAG)"
	scripts/verify-release-artifacts.sh "$(TAG)"
	git push origin HEAD:main
	git push origin "$(TAG)"

publish:
	scripts/publish-release.sh "$(TAG)"

release: check-release-ready package sign verify push-release publish

clean:
	rm -rf release-artifacts
