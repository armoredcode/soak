import os
import subprocess
import shutil
import json
import datetime

# Comprehensive Tool Mapping (Included Brakeman and Java)
TOOLS_MAPPING = {
    ".py": [
        ("bandit", ["bandit", "-r", ".", "-f", "json", "-o", "{OUTPUT}"]),
        (
            "semgrep_python",
            ["semgrep", "scan", "--json", "--output", "{OUTPUT}", "--config", "auto"],
        ),
    ],
    ".java": [
        (
            "pmd",
            [
                "pmd",
                "check",
                "-d",
                ".",
                "-f",
                "json",
                "-R",
                "rulesets/java/quickstart.xml",
                "-r",
                "{OUTPUT}",
            ],
        ),
        ("spotbugs", ["spotbugs", "-textui", "-json", "-output", "{OUTPUT}", "."]),
        (
            "semgrep_java",
            ["semgrep", "scan", "--json", "--output", "{OUTPUT}", "--config", "auto"],
        ),
    ],
    ".js": [
        ("eslint", ["eslint", ".", "-f", "json", "-o", "{OUTPUT}"]),
        ("njsscan", ["njsscan", ".", "--json", "--output", "{OUTPUT}"]),
        (
            "semgrep_js",
            ["semgrep", "scan", "--json", "--output", "{OUTPUT}", "--config", "auto"],
        ),
    ],
    ".go": [
        ("gosec", ["gosec", "-fmt=json", "-out={OUTPUT}", "./..."]),
        ("govulncheck", ["govulncheck", "-json", "./..."]),
    ],
    ".rb": [
        # Dawnscanner: General Ruby security analysis
        ("dawnscanner", ["dawn", "-j", "-f", "json", "."]),
        # Brakeman: Specialized Rails vulnerability scanner
        ("brakeman", ["brakeman", "-f", "json", "-o", "{OUTPUT}"]),
    ],
    ".sh": [("shellcheck", ["shellcheck", "-f", "json", "{FILE}"])],
    "Dockerfile": [
        (
            "trivy_config",
            ["trivy", "config", "--format", "json", "--output", "{OUTPUT}", "."],
        )
    ],
    "GLOBAL": [
        (
            "gitleaks",
            [
                "gitleaks",
                "detect",
                "--source",
                ".",
                "--format",
                "json",
                "--report-path",
                "{OUTPUT}",
                "--no-git",
            ],
        ),
        ("trivy_fs", ["trivy", "fs", "--format", "json", "--output", "{OUTPUT}", "."]),
    ],
}


def execute_tool(name, cmd_template, target_dir, report_path, current_file=None):
    final_cmd = [
        c.replace("{OUTPUT}", report_path).replace("{FILE}", str(current_file))
        for c in cmd_template
    ]

    if shutil.which(final_cmd[0]) is None:
        return {
            "tool": name,
            "status": "skipped",
            "reason": f"{final_cmd[0]} not found",
        }

    try:
        print(f"[>] Running {name}...")
        proc = subprocess.run(final_cmd, cwd=target_dir, capture_output=True, text=True)

        # Redirection for tools that output to stdout instead of file
        if "{OUTPUT}" not in " ".join(cmd_template):
            with open(report_path, "w") as f:
                f.write(proc.stdout)

        return {"tool": name, "exit_code": proc.returncode, "status": "completed"}
    except Exception as e:
        return {"tool": name, "status": "error", "message": str(e)}


def main():
    soak_version = os.getenv("SOAK_VERSION", "unknown-build")
    git_commit = os.getenv("SOAK_COMMIT", "none")
    git_branch = os.getenv("SOAK_BRANCH", "none")

    target_dir, reports_dir = "/src", "/reports"
    trigger_keys = set()
    sh_files = []

    for root, _, files in os.walk(target_dir):
        if any(x in root for x in ["node_modules", ".git", "venv"]):
            continue
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in TOOLS_MAPPING:
                trigger_keys.add(ext)

            # Context Triggers
            if ext == ".java":
                trigger_keys.add(".java")
            if ext == ".rb":
                trigger_keys.add(".rb")
            if f == "Gemfile":
                trigger_keys.add(".rb")
            if f in ["pom.xml", "build.gradle"]:
                trigger_keys.add(".java")
            if ext == ".sh":
                sh_files.append(os.path.join(root, f))
            if f == "Dockerfile":
                trigger_keys.add("Dockerfile")

    execution_log = []

    # 1. Global Tools
    for tool, cmd in TOOLS_MAPPING["GLOBAL"]:
        execution_log.append(
            execute_tool(
                tool, cmd, target_dir, os.path.join(reports_dir, f"global_{tool}.json")
            )
        )

    # 2. Language/Category Tools
    for key in trigger_keys:
        if key == ".sh":
            continue
        for tool, cmd in TOOLS_MAPPING[key]:
            report_name = f"{key.replace('.', '')}_{tool}.json"
            execution_log.append(
                execute_tool(
                    tool, cmd, target_dir, os.path.join(reports_dir, report_name)
                )
            )

    # 3. Shell scripts
    for i, sh_file in enumerate(sh_files[:10]):
        execution_log.append(
            execute_tool(
                f"shellcheck_{i}",
                TOOLS_MAPPING[".sh"][0][1],
                target_dir,
                os.path.join(reports_dir, f"sh_{i}.json"),
                current_file=sh_file,
            )
        )

    with open(os.path.join(reports_dir, "soak_summary.json"), "w") as f:
        json.dump(
            {
                "engine": f"SOAK {soak_version}",
                "scan_info": {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "target_commit": git_commit,
                    "target_branch": git_branch,
                },
                "results": execution_log,
            },
            f,
            indent=4,
        )


if __name__ == "__main__":
    if not os.path.exists("/reports"):
        os.makedirs("/reports")
    main()
