"""Verify system setup and configuration."""

import sys
from pathlib import Path
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_python_version() -> bool:
    """Check Python version."""
    print("Checking Python version...", end=" ")
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor} (requires 3.11+)")
        return False


def check_dependencies() -> bool:
    """Check if required packages are installed."""
    print("\nChecking dependencies...")
    required = [
        "fastapi",
        "uvicorn",
        "langchain",
        "langchain_google_genai",
        "langgraph",
        "faiss",
        "sqlalchemy",
        "pydantic",
        "pypdf",
        "docx2txt",
    ]

    all_installed = True
    for package in required:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (not installed)")
            all_installed = False

    return all_installed


def check_env_file() -> bool:
    """Check if .env file exists and has required variables."""
    print("\nChecking environment configuration...")
    env_file = Path(".env")

    if not env_file.exists():
        print("  ✗ .env file not found")
        print("    Run: cp .env.example .env")
        return False

    print("  ✓ .env file exists")

    # Check for required variables
    required_vars = ["GOOGLE_API_KEY"]
    with open(env_file, "r") as f:
        content = f.read()

    all_set = True
    for var in required_vars:
        if f"{var}=" in content:
            value = [line for line in content.split("\n") if line.startswith(f"{var}=")]
            if value and "your_" not in value[0] and value[0].split("=")[1].strip():
                print(f"  ✓ {var} is set")
            else:
                print(f"  ✗ {var} is not configured")
                all_set = False
        else:
            print(f"  ✗ {var} is missing")
            all_set = False

    return all_set


def check_directories() -> bool:
    """Check if required directories exist."""
    print("\nChecking directories...")
    directories = [
        "app",
        "prompts",
        "policies",
        "tests",
        "eval",
        "scripts",
        "kb",
    ]

    all_exist = True
    for directory in directories:
        path = Path(directory)
        if path.exists() and path.is_dir():
            print(f"  ✓ {directory}/")
        else:
            print(f"  ✗ {directory}/ (missing)")
            all_exist = False

    # Create data directories
    data_dirs = ["data", "data/indexes", "data/uploads"]
    for directory in data_dirs:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"  + Created {directory}/")

    return all_exist


def check_database() -> bool:
    """Check if database is initialized."""
    print("\nChecking database...")

    try:
        from app.db import engine
        from app.models.database import Base
        from sqlalchemy import inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if tables:
            print(f"  ✓ Database initialized ({len(tables)} tables)")
            return True
        else:
            print("  ✗ Database not initialized")
            print("    Run: python scripts/init_db.py")
            return False

    except Exception as e:
        print(f"  ✗ Database check failed: {e}")
        return False


def check_knowledge_base() -> bool:
    """Check if knowledge base has documents."""
    print("\nChecking knowledge base...")

    kb_dir = Path("kb")
    if not kb_dir.exists():
        print("  ! kb/ directory not found")
        return False

    files = list(kb_dir.glob("*.pdf")) + list(kb_dir.glob("*.docx")) + list(kb_dir.glob("*.md"))

    if files:
        print(f"  ✓ Found {len(files)} document(s) in kb/")
        return True
    else:
        print("  ! No documents in kb/")
        print("    Add .pdf/.docx files or use sample: kb/sample_channels.md")
        return False


def check_vector_store() -> bool:
    """Check if FAISS indexes exist."""
    print("\nChecking vector store...")

    indexes_dir = Path("data/indexes")
    if not indexes_dir.exists():
        print("  ! No indexes found")
        print("    Run: make ingest DOCS='./kb/*.pdf'")
        return False

    tenants = [d for d in indexes_dir.iterdir() if d.is_dir()]

    if tenants:
        print(f"  ✓ Found {len(tenants)} tenant index(es)")
        for tenant in tenants:
            index_file = tenant / "faiss.index"
            if index_file.exists():
                print(f"    - {tenant.name}/")
        return True
    else:
        print("  ! No tenant indexes")
        print("    Run: make ingest DOCS='./kb/*.pdf' TENANT=bank-asia")
        return False


def check_api_connectivity() -> bool:
    """Check if OpenAI API is accessible."""
    print("\nChecking OpenAI API connectivity...")

    try:
        from app.config import settings
        from openai import OpenAI

        if not settings.openai_api_key or "your_" in settings.openai_api_key:
            print("  ✗ OPENAI_API_KEY not configured")
            return False

        client = OpenAI(api_key=settings.openai_api_key)

        # Try to list models (lightweight check)
        try:
            client.models.list()
            print("  ✓ API key is valid and accessible")
            return True
        except Exception as e:
            print(f"  ✗ API check failed: {e}")
            return False

    except Exception as e:
        print(f"  ✗ Configuration error: {e}")
        return False


def print_summary(results: dict[str, bool]) -> None:
    """Print summary of checks."""
    print("\n" + "=" * 60)
    print("SETUP VERIFICATION SUMMARY")
    print("=" * 60)

    all_passed = all(results.values())
    critical = ["python_version", "dependencies", "env_file"]
    critical_passed = all(results.get(k, False) for k in critical)

    for check, passed in results.items():
        status = "✓" if passed else "✗"
        print(f"{status} {check.replace('_', ' ').title()}")

    print("=" * 60)

    if all_passed:
        print("✓ All checks passed! System is ready.")
        print("\nNext steps:")
        print("  1. Start server: make run")
        print("  2. View docs: http://localhost:8000/docs")
    elif critical_passed:
        print("⚠ Core system is ready, but some optional components need attention.")
        print("\nYou can start the server, but consider:")
        if not results.get("knowledge_base", True):
            print("  - Adding documents to kb/")
        if not results.get("vector_store", True):
            print("  - Running: make ingest DOCS='./kb/*.pdf'")
    else:
        print("✗ Critical issues found. Please fix them before running.")
        if not results.get("python_version", True):
            print("  - Upgrade to Python 3.11+")
        if not results.get("dependencies", True):
            print("  - Run: make install")
        if not results.get("env_file", True):
            print("  - Configure .env file")


def main() -> None:
    """Run all verification checks."""
    print("=" * 60)
    print("INTENT DETECTION SYSTEM - SETUP VERIFICATION")
    print("=" * 60)

    results = {}

    # Critical checks
    results["python_version"] = check_python_version()
    results["dependencies"] = check_dependencies()
    results["env_file"] = check_env_file()
    results["directories"] = check_directories()

    # Optional checks
    results["database"] = check_database()
    results["knowledge_base"] = check_knowledge_base()
    results["vector_store"] = check_vector_store()

    # API check (only if env is configured)
    if results["env_file"]:
        results["api_connectivity"] = check_api_connectivity()

    print_summary(results)

    # Exit code
    critical = ["python_version", "dependencies", "env_file"]
    sys.exit(0 if all(results.get(k, False) for k in critical) else 1)


if __name__ == "__main__":
    main()
