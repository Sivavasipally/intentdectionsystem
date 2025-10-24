"""Initialize database script."""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import init_db


def main() -> None:
    """Initialize database."""
    print("Initializing database...")

    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print(f"Created data directory: {data_dir.absolute()}")

    # Create indexes directory
    indexes_dir = data_dir / "indexes"
    indexes_dir.mkdir(exist_ok=True)
    print(f"Created indexes directory: {indexes_dir.absolute()}")

    # Create uploads directory
    uploads_dir = data_dir / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    print(f"Created uploads directory: {uploads_dir.absolute()}")

    try:
        init_db()
        print("\n✓ Database initialized successfully!")
        print(f"✓ Database location: {(data_dir / 'app.db').absolute()}")

    except Exception as e:
        print(f"\n✗ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
