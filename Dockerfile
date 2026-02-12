FROM registry.opensuse.org/opensuse/tumbleweed:latest

ENV DEBIAN_FRONTEND=noninteractive
ENV GOPATH=/root/go
ENV PATH=$PATH:$GOPATH/bin:/usr/local/bin:/opt/pmd/bin:/opt/spotbugs/bin

# 1. Install Runtimes & Build Tools

# 1. Install Runtimes & System Build Tools
RUN zypper --non-interactive refresh && \
    zypper --non-interactive install -y \
    unzip python313 python313-pip nodejs npm go rust cargo \
    ruby ruby-devel gcc make git curl shadow which \
    java-17-openjdk-headless cppcheck flawfinder ShellCheck && \
    zypper clean -a

# 2. Fix PEP 668 & Install Python-based SAST/SCA
# Usiamo --break-system-packages perché siamo in un container dedicato
RUN pip install --upgrade pip --break-system-packages && \
    pip install --break-system-packages \
    bandit mypy checkov njsscan semgrep pip-audit radon 

# 3. Install Java SAST Tools (PMD & SpotBugs)
RUN curl -sSLo pmd.zip https://github.com/pmd/pmd/releases/download/pmd_releases%2F7.0.0/pmd-dist-7.0.0-bin.zip && \
    unzip pmd.zip -d /opt/ && mv /opt/pmd-bin-7.0.0 /opt/pmd && rm pmd.zip

RUN curl -sSLo spotbugs.zip https://github.com/spotbugs/spotbugs/releases/download/4.8.3/spotbugs-4.8.3.zip && \
    unzip spotbugs.zip -d /opt/ && mv /opt/spotbugs-4.8.3 /opt/spotbugs && rm spotbugs.zip

# 4. Install Ruby-based tools (Dawnscanner by thesp0nge)
RUN gem install dawnscanner brakeman

# 5. Install Go-based tools
RUN go install github.com/securego/gosec/v2/cmd/gosec@latest && \
    go install golang.org/x/vuln/cmd/govulncheck@latest && \
    go install github.com/terraform-linters/tflint@latest

# 6. Install Binary & Secrets scanners
RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin && \
    curl -sSLo gitleaks.tar.gz https://github.com/gitleaks/gitleaks/releases/download/v8.18.1/gitleaks_8.18.1_linux_x64.tar.gz && \
    tar -xzf gitleaks.tar.gz && mv gitleaks /usr/local/bin/

# 7. Hadolint per Dockerfile
RUN curl -sSLo /usr/local/bin/hadolint https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Linux-x86_64 && \
    chmod +x /usr/local/bin/hadolint

WORKDIR /src
RUN mkdir -p /reports

COPY analyzer.py /usr/local/bin/analyzer.py
RUN chmod +x /usr/local/bin/analyzer.py

ENTRYPOINT ["python3", "/usr/local/bin/analyzer.py"]
