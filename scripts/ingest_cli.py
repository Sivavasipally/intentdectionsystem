"""CLI script for document ingestion."""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import get_db
from app.services.ingestion import ingestion_service


def main() -> None:
    """Run document ingestion from CLI."""
    parser = argparse.ArgumentParser(description="Ingest documents into knowledge base")
    parser.add_argument("files", nargs="+", help="Document files to ingest")
    parser.add_argument("--tenant", default="bank-asia", help="Tenant identifier")
    parser.add_argument("--doc-type", default="general", help="Document type")
    parser.add_argument("--department", help="Department")
    parser.add_argument("--country", help="Country")
    parser.add_argument("--version", help="Document version")

    args = parser.parse_args()

    # Expand glob patterns
    file_paths = []
    for pattern in args.files:
        paths = list(Path().glob(pattern))
        file_paths.extend([str(p.absolute()) for p in paths if p.is_file()])

    if not file_paths:
        print("Error: No files found")
        sys.exit(1)

    print(f"Found {len(file_paths)} file(s) to ingest")

    # Prepare metadata
    metadata = {
        "doc_type": args.doc_type,
        "department": args.department,
        "country": args.country,
        "version": args.version,
    }

    # Ingest documents
    try:
        with get_db() as db:
            total_docs, total_chunks, index_path = ingestion_service.ingest_documents(
                file_paths=file_paths,
                tenant=args.tenant,
                db=db,
                metadata=metadata,
            )

        print("\n" + "=" * 60)
        print("INGESTION COMPLETE")
        print("=" * 60)
        print(f"Documents processed: {total_docs}")
        print(f"Chunks created: {total_chunks}")
        print(f"Index path: {index_path}")
        print("=" * 60)

    except Exception as e:
        print(f"\nError during ingestion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
