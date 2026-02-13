#!/usr/bin/env python3
import os, subprocess, shutil, sys, argparse, datetime, tempfile

VERSION = "1.1.1"
IMAGE_NAME = "soak-engine"


def get_runtime():
    if shutil.which("podman"):
        return "podman"
    if shutil.which("docker"):
        return "docker"
    return None


def get_git_metadata(path):
    try:
        commit = subprocess.check_output(
            ["git", "-C", path, "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        branch = subprocess.check_output(
            ["git", "-C", path, "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return commit, branch
    except:
        return "none", "none"


def check_updates():
    """Checks for script updates and image age."""
    print(f"\033[90m[UPDATE CHECK] Testing for new versions...\033[0m")

    # 1. Check Image Age
    runtime = get_runtime()
    try:
        inspect_cmd = [runtime, "inspect", "-f", "{{.Created}}", IMAGE_NAME]
        created_str = subprocess.check_output(
            inspect_cmd, stderr=subprocess.DEVNULL, text=True
        ).strip()
        # Handle different date formats from Docker/Podman
        created_date = datetime.datetime.fromisoformat(created_str.split("T")[0])
        age_days = (datetime.datetime.now() - created_date).days

        if age_days > 14:
            print(
                f"\033[93m[!] Engine is {age_days} days old. Run ./setup.sh to refresh tools.\033[0m"
            )
    except:
        print(f"\033[91m[!] Engine not found. Please run ./setup.sh first.\033[0m")

    # 2. Check Git Origin (if in a repo)
    try:
        subprocess.run(["git", "fetch"], stderr=subprocess.DEVNULL, timeout=3)
        status = subprocess.check_output(["git", "status", "-uno"], text=True)
        if "your branch is behind" in status.lower():
            print(
                f"\033[93m[!] A newer version of SOAK is available on GitHub! Run 'git pull'.\033[0m"
            )
    except:
        pass  # Skip if no network or not a git repo


def run():
    runtime = get_runtime()
    if not runtime:
        print("\033[91m[ERROR] No container runtime found.\033[0m")
        sys.exit(1)

    parser = argparse.ArgumentParser(description=f"SOAK CLI v{VERSION}")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("-o", "--output", default="./soak_reports")
    parser.add_argument(
        "--update", action="store_true", help="Manually trigger update check"
    )
    args = parser.parse_args()

    # Automatic update check (silent/fast)
    if args.update or datetime.datetime.now().second % 10 == 0:  # Check occasionally
        check_updates()

    # --- Path Management (The Colon Fix) ---
    target_abs = os.path.abspath(args.path)
    reports_abs = os.path.abspath(args.output)
    os.makedirs(reports_abs, exist_ok=True)

    tmp_link = None
    mount_target = target_abs

    if ":" in target_abs:
        # tmp_link = os.path.join(tempfile.gettempdir(), f"soak_safe_{os.getpid()}")
        safe_base = os.path.expanduser("~/.soak_tmp")
        os.makedirs(safe_base, exist_ok=True)
        tmp_link = os.path.join(safe_base, f"link_{os.getpid()}")
        os.symlink(target_abs, tmp_link)
        mount_target = tmp_link

    commit, branch = get_git_metadata(target_abs)

    cmd = [
        runtime,
        "run",
        "--rm",
        "-e",
        f"SOAK_VERSION={VERSION}",
        "-e",
        f"SOAK_COMMIT={commit}",
        "-e",
        f"SOAK_BRANCH={branch}",
    ]

    if runtime == "podman":
        cmd += [
            "--userns=keep-id",
            "-v",
            f"{mount_target}:/src:Z",
            "-v",
            f"{reports_abs}:/reports:Z",
        ]
        cmd += ["--security-opt", "label=disable"]
    else:
        cmd += [
            "-u",
            f"{os.getuid()}:{os.getgid()}",
            "-v",
            f"{mount_target}:/src",
            "-v",
            f"{reports_abs}:/reports",
        ]

    cmd.append(IMAGE_NAME)

    print(f"\033[94mSOAK v{VERSION}\033[0m | \033[93m{runtime.upper()}\033[0m")
    print(f"\033[90mTarget: {target_abs} @ {commit}\033[0m\n")

    try:
        subprocess.run(cmd, check=True)
        print(f"\n\033[92m[SUCCESS] Analysis complete.\033[0m")
    except Exception as e:
        print(f"\n\033[91m[ERROR] Runtime error: {e}\033[0m")


if __name__ == "__main__":
    run()
