# SOAK

### **Deep-Tissue Static Analysis. One Command, Total Coverage.**

[![Engine](https://img.shields.io/badge/Engine-openSUSE%20Tumbleweed-f86036?logo=opensuse)](https://www.opensuse.org/)
[![License](https://img.shields.io/badge/License-AGPL%203.0-red.svg)](LICENSE)

**SOAK** is a powerful, zero-dependency static analysis orchestrator designed to
"drown" bugs and vulnerabilities before they reach production. By wrapping the
world's most trusted security tools into a single, high-performance **openSUSE
Tumbleweed** container, SOAK provides a deep-tissue scan of your codebase
without cluttering your local environment.

---

## 🚀 Why SOAK?

Security tooling is often fragmented. Developers have to manage different
runtimes (Python, Go, Ruby, Java) just to run basic linters. **SOAK changes
that.**

- **Zero Setup:** If you have Docker, you have SOAK. No need to install dozens
  of security binaries.
- **Multi-Engine:** It orchestrates a "Chimera" of scanners (Semgrep, Gitleaks,
  Brakeman, etc.) for maximum coverage.
- **Rolling Edge:** Built on **openSUSE Tumbleweed**, it uses the latest,
  bleeding-edge versions of security engines.
- **Deep-Tissue SCA:** It "soaks" into your dependencies to find known CVEs.

---

## 🛠 Supported Ecosystems & Tools

| Category           | Tools Integrated                               |
| :----------------- | :--------------------------------------------- |
| **Multi-Language** | **Semgrep**, **Trivy**                         |
| **Python**         | **Bandit**, **Mypy**, **Radon**, **Pip-audit** |
| **Ruby**           | **Dawnscanner** (by thesp0nge), **Brakeman**   |
| **Java**           | **PMD**, **SpotBugs**                          |
| **Go**             | **Gosec**, **Govulncheck**, **Staticcheck**    |
| **Secrets**        | **Gitleaks**                                   |
| **Infrastructure** | **Hadolint**, **Checkov**, **ShellCheck**      |

---

## 💻 Quick Start

### 1. Install

Clone the repo and run the setup script:

```bash
chmod +x setup.sh
./setup.sh
```

### 2. Run

Simply point SOAK at your project directory:

```sh
soak /home/user/my-awesome-project
```

## 🤖 CI/CD Integration (GitHub Actions)

You can easily integrate SOAK into your CI/CD pipeline. Here is an example of a
workflow file (.github/workflows/security.yml):

```yml
name: Security Scan with SOAK

on: [push, pull_request]

jobs:
  soak-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Build SOAK Engine
        run:
          docker build -t soak-engine
          [https://github.com/yourusername/soak.git](https://github.com/yourusername/soak.git)

      - name: Run SOAK Scan
        run: |
          mkdir -p reports
          docker run --rm \
            -v ${{ github.workspace }}:/src \
            -v $(pwd)/reports:/reports \
            soak-engine

      - name: Upload Scan Results
        uses: actions/upload-artifact@v3
        with:
          name: soak-security-reports
          path: reports/
```

## 🏗 Architecture

SOAK follows a three-layered analysis pattern:

Detection Layer: Automatically identifies languages and build systems (pom.xml,
Gemfile, go.mod).

Execution Layer: Spawns isolated processes for each relevant tool inside a
Tumbleweed container.

Aggregation Layer: Collects raw JSON data and generates a soak_summary.json.

## 🧪 Acknowledgments

SOAK stands on the shoulders of giants. Special thanks to the open-source
security community and tools maintainers.

## 📜 License

Distributed under the GNU Affero General Public License v3.0. See LICENSE for
more information.
