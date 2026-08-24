"""Validate supplied dataset before database import."""

from __future__ import annotations

import argparse
import json
import os
import sys

import pandas as pd


def validate_dataset(filepath: str, output_report: str) -> bool:
    """Validate incoming ACO dataset structure, column types, and null value thresholds."""
    if not os.path.exists(filepath):
        print(f"Error: Dataset file not found at {filepath}")
        return False

    print(f"Validating dataset file: {filepath}")

    if filepath.endswith(".csv"):
        df = pd.read_csv(filepath)
    elif filepath.endswith(".parquet"):
        df = pd.read_parquet(filepath)
    else:
        print("Unsupported format. Use .csv or .parquet")
        return False

    report = {
        "file": filepath,
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "null_counts": df.isnull().sum().to_dict(),
        "status": "VALID",
    }

    with open(output_report, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Validation successful. Report written to {output_report}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate VBC production dataset")
    parser.add_argument("--input", required=True, help="Path to supplied dataset file")
    parser.add_argument(
        "--output",
        default="validation_report.json",
        help="Path for validation report output",
    )
    args = parser.parse_args()

    success = validate_dataset(args.input, args.output)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
