#!/usr/bin/env python3
import os, subprocess, sys, argparse

VERSION = "1.0.0"


def get_git_metadata(path):
    """Extracts git hash and branch from the target directory."""
    try:
        # Get short hash
        commit = subprocess.check_output(
            ["git", "-C", path, "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        # Get branch name
        branch = subprocess.check_output(
            ["git", "-C", path, "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return commit, branch
    except Exception:
        return "none", "none"


def run():
    parser = argparse.ArgumentParser(description="SOAK CLI")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("-o", "--output", default="./soak_reports")
    args = parser.parse_args()

    target = os.path.abspath(args.path)
    reports = os.path.abspath(args.output)
    commit, branch = get_git_metadata(target)
    if not os.path.exists(reports):
        os.makedirs(reports)

    print(f"\033[94mSOAKing v{VERSION} is absorbing: {target}...\033[0m")

    cmd = [
        "docker",
        "run",
        "--rm",
        "-u",
        f"{os.getuid()}:{os.getgid()}",
        "-e",
        f"SOAK_VERSION={VERSION}",
        "-e",
        f"SOAK_COMMIT={commit}",
        "-e",
        f"SOAK_BRANCH={branch}",
        "-v",
        f"{target}:/src",
        "-v",
        f"{reports}:/reports",
        "soak-engine",
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"\033[92m[DONE] Reports saved in: {reports}\033[0m")
    except Exception as e:
        print(f"\033[91m[ERROR] Scan failed: {e}\033[0m")


if __name__ == "__main__":
    run()
