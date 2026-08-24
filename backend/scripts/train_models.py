"""Offline model training entrypoint.

Phase 12 implementation. Requires supplied YAML configs and training data in PostgreSQL.
Training never runs inside API request handlers.
"""

from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Train VBC ML models offline")
    parser.add_argument(
        "--config",
        required=True,
        help="Path to supplied ML YAML configuration",
    )
    args = parser.parse_args()

    print(
        "train_models.py is not yet implemented.\n"
        f"Config: {args.config}\n"
        "Awaiting ML YAML and approved training pipeline (Phase 12)."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
