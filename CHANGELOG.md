# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2026-02-13

### Fixed

- The Colon Trap: Resolved the incorrect volume format error caused by host
  paths containing colons (:) by implementing a temporary safe symbolic link in
  /tmp. This ensures stability across different storage drivers without
  modifying original folder names.

- Path Sanitization: Enforced absolute path resolution using os.path.abspath to
  prevent volume mounting issues on strictly-configured container runtimes.

### Added

- Integrated Update Engine: Added a multi-tier update checker that monitors both
  the Tumbleweed image age (notifying if tools are >14 days old) and Git origin
  (checking for new script versions on GitHub).

- Full Traceability: Re-integrated and improved get_git_metadata to pass the
  target's commit hash and branch name into the container for comprehensive
  security auditing.

## [1.1.0] - 2026-02-13

### Added

- Smart Runtime Detection: soak.py now automatically detects and uses podman or
  docker.
- Git Traceability: Automatic extraction of Git commit hash and branch name from
  the target directory, included in reports.
- Auto-Update Logic: The CLI now checks if the engine image is older than 14
  days and notifies the user to run setup.sh.

- Git Sync Check: Integration with git fetch to alert users if a newer version
  of the SOAK script is available on GitHub.

- SELinux Support: Added :Z volume flags and --userns=keep-id for rootless
  Podman compatibility.

- Complexity Analysis: Integrated Radon for Python cyclomatic complexity
  metrics.

### Changed

- Branding: Official project name set to SOAK (Static Analysis Orchestrator).

- Dynamic Versioning: Versioning is now handled via environment variables passed
  to the container instead of being hardcoded in analyzer.py.

## [1.0.2] - 2026-02-12

### Added

- Java Ecosystem Support: Integrated PMD and SpotBugs.
- Ruby Deep Scan: Added Brakeman specifically for Ruby on Rails security
  analysis.
- Universal SCA: Integrated Trivy and pip-audit for software composition
  analysis and dependency checking.

- Infrastructure Scanning: Added Hadolint for Dockerfile linting and ShellCheck
  for shell script analysis.

### Fixed

- Fixed a bug where unzip was missing in the Tumbleweed base image, preventing
  Java tools installation.

- Resolved permission issues when running Docker as root by mapping UID:GID in
  the wrapper.

## [1.0.1] - 2026-02-11

### Changed

- Base OS: Switched from openSUSE Leap to openSUSE Tumbleweed to ensure
  bleeding-edge security tool versions.
- Licensing: Project licensed under GNU AGPL 3.0.
- Integrated Dawnscanner for specialized Ruby security scanning.
- Secrets Detection: Integrated Gitleaks as a global scanner.
- Go Support: Added Gosec and Govulncheck.

## [1.0.0] - 2026-02-10

### Added

- Initial release of the static analysis orchestrator.
- Support for Python (Bandit) and JavaScript (njsscan).
- Semgrep integration with auto-config mode.
- Basic JSON report generation and master index summary.
- Docker-based execution environment.
