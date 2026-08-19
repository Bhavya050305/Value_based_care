"""Demo data seeding is intentionally disabled.

Per project policy: no fake, mock, or fabricated business data may be inserted
into development, staging, or production databases.

Use isolated test fixtures in automated tests only (tests/ directory).
"""

from __future__ import annotations

import sys


def main() -> int:
    print(
        "seed_demo_data.py is disabled.\n"
        "This project does not seed fake ACO, financial, quality, or ML data.\n"
        "Populate the database via scripts/import_data.py with the supplied production dataset."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
