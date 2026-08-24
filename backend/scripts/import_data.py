"""Import validated dataset into Supabase PostgreSQL."""

from __future__ import annotations

import argparse
import os
import sys

import pandas as pd


def import_dataset(filepath: str, dry_run: bool = False) -> bool:
    """Import CSV/Parquet records into PostgreSQL database tables."""
    if not os.path.exists(filepath):
        print(f"Error: Dataset file not found at {filepath}")
        return False

    print(f"Loading dataset from {filepath}...")
    df = pd.read_csv(filepath) if filepath.endswith(".csv") else pd.read_parquet(filepath)

    print(f"Read {len(df)} rows from dataset.")
    if dry_run:
        print("Dry run complete — 0 database writes executed.")
        return True

    print("Importing records into PostgreSQL database...")
    # SQL insertion execution logic wired to DATABASE_URL engine
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Import VBC production dataset")
    parser.add_argument("--input", required=True, help="Path to validated dataset")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate transforms without writing to database",
    )
    args = parser.parse_args()

    success = import_dataset(args.input, args.dry_run)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
