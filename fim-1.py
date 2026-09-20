#!/usr/bin/env python3
"""
Simple File Integrity Monitoring (FIM) tool.

Features:
- Create a baseline of SHA-256 hashes for files in a directory
- Monitor the directory continuously
- Detect MODIFIED, DELETED, and ADDED files
- Store the trusted baseline in baseline.txt

Usage:
    python fim.py baseline <directory>
    python fim.py monitor <directory> [--interval SECONDS]

Examples:
    python fim.py baseline ./protected_files
    python fim.py monitor ./protected_files --interval 5
"""

import argparse
import hashlib
import time
from pathlib import Path

BASELINE_FILE = Path("baseline.txt")


def calculate_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256 = hashlib.sha256()

    try:
        with file_path.open("rb") as f:
            while True:
                chunk = f.read(1024 * 1024)  # Read 1 MB at a time
                if not chunk:
                    break
                sha256.update(chunk)

        return sha256.hexdigest()

    except (PermissionError, OSError) as e:
        print(f"[!] Could not hash {file_path}: {e}")
        return ""


def collect_files(directory: Path) -> dict:
    """Return {relative_file_path: SHA-256 hash} for all files."""
    files = {}

    for file_path in directory.rglob("*"):
        if not file_path.is_file():
            continue

        # Do not include the baseline inside the monitored directory.
        try:
            relative_path = file_path.relative_to(directory)
        except ValueError:
            continue

        file_hash = calculate_hash(file_path)

        if file_hash:
            files[str(relative_path)] = file_hash

    return files


def save_baseline(hashes: dict) -> None:
    """Save file/hash pairs to baseline.txt."""
    with BASELINE_FILE.open("w", encoding="utf-8") as f:
        for file_path, file_hash in sorted(hashes.items()):
            f.write(f"{file_hash}  {file_path}\n")


def load_baseline() -> dict:
    """Load file/hash pairs from baseline.txt."""
    if not BASELINE_FILE.exists():
        return {}

    hashes = {}

    with BASELINE_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            try:
                file_hash, file_path = line.split("  ", 1)
                hashes[file_path] = file_hash
            except ValueError:
                print(f"[!] Ignoring invalid baseline line: {line}")

    return hashes


def create_baseline(directory: Path) -> None:
    """Create a new trusted baseline."""
    if not directory.exists() or not directory.is_dir():
        print(f"[!] Directory does not exist: {directory}")
        return

    print(f"[*] Creating baseline for: {directory.resolve()}")

    hashes = collect_files(directory)
    save_baseline(hashes)

    print(f"[+] Baseline created: {BASELINE_FILE.resolve()}")
    print(f"[+] Files recorded: {len(hashes)}")


def check_integrity(directory: Path, baseline: dict) -> bool:
    """Compare current files with the trusted baseline."""
    current = collect_files(directory)

    changed = []
    deleted = []
    added = []

    # Files that existed in the baseline
    for file_path, old_hash in baseline.items():
        if file_path not in current:
            deleted.append(file_path)
        elif current[file_path] != old_hash:
            changed.append(file_path)

    # Files that were not in the baseline
    for file_path in current:
        if file_path not in baseline:
            added.append(file_path)

    if not changed and not deleted and not added:
        print("[OK] No integrity changes detected.")
        return True

    print("\n" + "=" * 60)
    print("FILE INTEGRITY ALERT")
    print("=" * 60)

    if changed:
        print("\n[MODIFIED]")
        for file_path in changed:
            print(f"  - {file_path}")

    if deleted:
        print("\n[DELETED]")
        for file_path in deleted:
            print(f"  - {file_path}")

    if added:
        print("\n[ADDED]")
        for file_path in added:
            print(f"  - {file_path}")

    print("\n[!] Possible file integrity change detected.")
    print("=" * 60)

    return False


def monitor(directory: Path, interval: int) -> None:
    """Continuously monitor the directory."""
    baseline = load_baseline()

    if not baseline:
        print("[!] No baseline found.")
        print("[!] Run:")
        print(f"    python fim.py baseline {directory}")
        return

    print(f"[*] Monitoring: {directory.resolve()}")
    print(f"[*] Check interval: {interval} seconds")
    print("[*] Press Ctrl+C to stop.\n")

    try:
        while True:
            check_integrity(directory, baseline)
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n[*] Monitoring stopped.")


def main():
    parser = argparse.ArgumentParser(
        description="Simple Python File Integrity Monitoring (FIM) tool"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Baseline command
    baseline_parser = subparsers.add_parser(
        "baseline",
        help="Create a new SHA-256 baseline"
    )
    baseline_parser.add_argument(
        "directory",
        help="Directory containing files to monitor"
    )

    # Monitor command
    monitor_parser = subparsers.add_parser(
        "monitor",
        help="Continuously monitor files"
    )
    monitor_parser.add_argument(
        "directory",
        help="Directory to monitor"
    )
    monitor_parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Seconds between checks (default: 5)"
    )

    args = parser.parse_args()
    directory = Path(args.directory)

    if args.command == "baseline":
        create_baseline(directory)

    elif args.command == "monitor":
        monitor(directory, args.interval)


if __name__ == "__main__":
    main()
