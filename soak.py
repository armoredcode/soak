#!/usr/bin/env python3
import os, subprocess, shutil, sys, argparse, datetime, time

# Versioning and Engine naming
VERSION = "1.1.2"
IMAGE_NAME = "soak-engine"
# Generate a unique container name to prevent collisions during concurrent runs
CONTAINER_NAME = f"soak_worker_{int(time.time())}"


def get_runtime():
    """Detects available container runtime, prioritizing Podman over Docker."""
    if shutil.which("podman"):
        return "podman"
    if shutil.which("docker"):
        return "docker"
    return None


def get_git_metadata(path):
    """Extracts the git commit hash and branch name from the target project."""
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
    except Exception:
        # Return fallback values if the target is not a git repository
        return "none", "none"


def check_updates(runtime):
    """Verifies if the container image or the SOAK script itself are outdated."""
    print(f"\033[90m[UPDATE] Checking system freshness...\033[0m")
    try:
        # Check Image age (SAST tools change frequently)
        inspect_fmt = "{{.Created}}" if runtime == "docker" else "{{.CreatedAt}}"
        res = subprocess.check_output(
            [runtime, "inspect", "-f", inspect_fmt, IMAGE_NAME],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        # Parse the date string to calculate age in days
        created_date = datetime.datetime.fromisoformat(res.split("T")[0])
        age = (datetime.datetime.now() - created_date).days
        if age > 14:
            print(
                f"\033[93m[!] Engine is {age} days old. Run ./setup.sh to update tools.\033[0m"
            )

        # Check local SOAK repository status against GitHub
        script_dir = os.path.dirname(os.path.realpath(__file__))
        subprocess.run(
            ["git", "-C", script_dir, "fetch"], stderr=subprocess.DEVNULL, timeout=2
        )
        status = subprocess.check_output(
            ["git", "-C", script_dir, "status", "-uno"], text=True
        )
        if "your branch is behind" in status.lower():
            print(
                f"\033[93m[!] A newer SOAK version is available. Run 'git pull'.\033[0m"
            )
    except Exception:
        pass  # Silently fail if there is no internet connection or git repo


def run():
    runtime = get_runtime()
    if not runtime:
        print(
            "\033[91m[ERROR] No container runtime (podman/docker) found in PATH.\033[0m"
        )
        sys.exit(1)

    parser = argparse.ArgumentParser(description=f"SOAK CLI v{VERSION}")
    parser.add_argument("path", nargs="?", default=".", help="Target directory to scan")
    parser.add_argument(
        "-o",
        "--output",
        default="./soak_reports",
        help="Directory for analysis reports",
    )
    parser.add_argument(
        "--skip-update", action="store_true", help="Skip the automatic update check"
    )
    args = parser.parse_args()

    # Define absolute paths for host source and report directories
    target_abs = os.path.abspath(args.path)
    reports_abs = os.path.abspath(args.output)
    os.makedirs(reports_abs, exist_ok=True)

    # 1. Capture target context (Git metadata)
    commit, branch = get_git_metadata(target_abs)

    # 2. Run update check (throttled to run occasionally)
    if not args.skip_update and datetime.datetime.now().second % 20 == 0:
        check_updates(runtime)

    # UI Branding and metadata display
    print(
        f"\033[94mSOAK v{VERSION}\033[0m | Mode: \033[93mZero-Mount (Direct Injection)\033[0m"
    )
    print(f"\033[90mTarget: {target_abs} @ {commit}\033[0m\n")

    try:
        # 3. Create the container without mounting host volumes.
        # This bypasses "rootfs remount-private: permission denied" errors.
        # We pass metadata via environment variables for the internal analyzer.
        subprocess.run(
            [
                runtime,
                "create",
                "--name",
                CONTAINER_NAME,
                "-e",
                f"SOAK_VERSION={VERSION}",
                "-e",
                f"SOAK_COMMIT={commit}",
                "-e",
                f"SOAK_BRANCH={branch}",
                IMAGE_NAME,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )

        # 4. Inject target files directly into the container filesystem.
        # The '/.' syntax ensures we copy the content of the folder, not the folder itself.
        print("\033[90m[1/3] Injecting source code into container...\033[0m")
        subprocess.run(
            [runtime, "cp", f"{target_abs}/.", f"{CONTAINER_NAME}:/src/"], check=True
        )

        # 5. Execute the analysis by starting the container.
        print("\033[90m[2/3] Absorbing vulnerabilities...\033[0m")
        subprocess.run([runtime, "start", "-a", CONTAINER_NAME], check=True)

        # 6. Extract the generated reports back to the host machine.
        print("\033[90m[3/3] Extracting reports...\033[0m")
        subprocess.run(
            [runtime, "cp", f"{CONTAINER_NAME}:/reports/.", reports_abs], check=True
        )

        print(
            f"\n\033[92m[SUCCESS] Scan complete. Check your results in: {reports_abs}\033[0m"
        )

    except Exception as e:
        print(f"\n\033[91m[ERROR] Workflow failed: {e}\033[0m")
    finally:
        # 7. Cleanup: Ensure the worker container is removed even if the scan fails.
        subprocess.run(
            [runtime, "rm", "-f", CONTAINER_NAME],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )


if __name__ == "__main__":
    run()
