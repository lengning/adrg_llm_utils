#!/usr/bin/env python3
"""
Convert renv.lock -> R_Packages_And_Versions.csv

Usage:
  python renv_to_csv.py --renv renv.lock \
      --out adrg/llm-adrg-out/R_Packages_And_Versions.csv

Defaults:
  --out defaults to adrg/llm-adrg-out/R_Packages_And_Versions.csv
"""

import argparse
import csv
import json
import os
import sys

def load_renv(renv_path: str) -> dict:
    try:
        with open(renv_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        sys.exit(f"ERROR: renv.lock not found at: {renv_path}")
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: renv.lock is not valid JSON ({e}).")

def extract_packages(renv: dict):
    # renv.lock usually stores packages under "Packages"
    pkgs = renv.get("Packages") or renv.get("packages")
    if not isinstance(pkgs, dict):
        sys.exit("ERROR: Could not find a 'Packages' section in renv.lock.")
    rows = []
    for name, meta in pkgs.items():
        # Skip the R runtime entry if present
        if name.lower() == "r":
            continue
        version = (
            (meta.get("Version") or meta.get("version") or "").strip()
            if isinstance(meta, dict)
            else ""
        )
        rows.append((name, version))
    # Sort by package name (case-insensitive) for determinism
    rows.sort(key=lambda x: x[0].lower())
    return rows

def write_csv(rows, out_path: str):
    # If out_path is '-' or None, write to stdout
    if out_path is None or out_path == "-":
        w = csv.writer(sys.stdout)
        w.writerow(["Package", "Version"])
        for pkg, ver in rows:
            w.writerow([pkg, ver])
        return

    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Package", "Version"])
        for pkg, ver in rows:
            w.writerow([pkg, ver])

def main():
    parser = argparse.ArgumentParser(description="Convert renv.lock -> R_Packages_And_Versions.csv")
    parser.add_argument("--renv", required=True, help="Path to renv.lock")
    parser.add_argument("--out", help="Output CSV path. If omitted, uses $R_PACKAGES_OUT or places R_Packages_And_Versions.csv next to the renv.lock. Use '-' to write to stdout.")
    args = parser.parse_args()

    renv = load_renv(args.renv)
    rows = extract_packages(renv)

    # Determine output path: precedence = --out, $R_PACKAGES_OUT, next-to-renv
    out_path = args.out or os.environ.get("R_PACKAGES_OUT")
    if not out_path:
        renv_dir = os.path.dirname(os.path.abspath(args.renv)) or "."
        out_path = os.path.join(renv_dir, "R_Packages_And_Versions.csv")

    write_csv(rows, out_path)
    if out_path == "-":
        print(f"Wrote CSV to stdout ({len(rows)} packages).")
    else:
        print(f"Wrote {out_path} ({len(rows)} packages).")

if __name__ == "__main__":
    main()
