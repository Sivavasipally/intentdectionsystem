"""Helper script to fix OpenAI API key issues."""

import os
from pathlib import Path

print("=" * 60)
print("OpenAI API Key Fix Tool")
print("=" * 60)
print()

# Check current .env file
env_file = Path(".env")

if env_file.exists():
    print("✓ .env file found")
    print()
    print("Current .env content:")
    print("-" * 60)
    with open(env_file, "r") as f:
        for line in f:
            if "OPENAI_API_KEY" in line:
                # Show masked key
                if "=" in line:
                    key = line.split("=")[1].strip()
                    if key and len(key) > 10:
                        masked = f"{key[:10]}...{key[-4:]}"
                        print(f"OPENAI_API_KEY={masked} (length: {len(key)} chars)")
                    else:
                        print(f"OPENAI_API_KEY={key} (⚠️ Too short!)")
                else:
                    print(line.strip())
    print("-" * 60)
    print()
else:
    print("✗ .env file NOT found!")
    print()
    response = input("Create .env from .env.example? (y/n): ")
    if response.lower() == 'y':
        with open(".env.example", "r") as src:
            with open(".env", "w") as dst:
                dst.write(src.read())
        print("✓ Created .env file")
    else:
        print("Please create .env file first!")
        exit(1)

print()
print("=" * 60)
print("Getting a New OpenAI API Key")
print("=" * 60)
print()
print("1. Open your browser and go to:")
print("   https://platform.openai.com/api-keys")
print()
print("2. Sign in to your OpenAI account")
print()
print("3. Click '+ Create new secret key'")
print()
print("4. Name it: IntentDetectionSystem")
print()
print("5. Click 'Create secret key'")
print()
print("6. COPY THE ENTIRE KEY (it only shows once!)")
print()
print("=" * 60)
print()

# Get new key from user
print("Paste your NEW OpenAI API key here:")
print("(It should start with 'sk-proj-' or 'sk-' and be 50-60 chars long)")
print()
new_key = input("API Key: ").strip()

# Validate key format
if not new_key:
    print("\n✗ No key provided!")
    exit(1)

if not (new_key.startswith("sk-proj-") or new_key.startswith("sk-")):
    print("\n⚠️ Warning: Key doesn't start with 'sk-proj-' or 'sk-'")
    print("Are you sure this is correct?")
    response = input("Continue anyway? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        exit(1)

if len(new_key) < 40:
    print(f"\n⚠️ Warning: Key seems too short ({len(new_key)} chars)")
    print("A valid OpenAI key is usually 50-60 characters long")
    response = input("Continue anyway? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        exit(1)

print()
print("-" * 60)
print(f"Key length: {len(new_key)} characters")
print(f"Key starts with: {new_key[:15]}...")
print(f"Key ends with: ...{new_key[-4:]}")
print("-" * 60)
print()

# Test the key
print("Testing API key with OpenAI...")
try:
    from openai import OpenAI
    client = OpenAI(api_key=new_key)
    models = list(client.models.list())
    print(f"✓ SUCCESS! API key is valid!")
    print(f"✓ Found {len(models)} available models")
    print()
except Exception as e:
    print(f"✗ ERROR: API key test failed!")
    print(f"Error: {e}")
    print()
    print("This key is still invalid. Please:")
    print("1. Make sure you copied the ENTIRE key")
    print("2. Go to https://platform.openai.com/account/billing")
    print("3. Verify you have a payment method added")
    print("4. Try creating a new key")
    exit(1)

# Update .env file
print("Updating .env file...")
with open(env_file, "r") as f:
    lines = f.readlines()

with open(env_file, "w") as f:
    updated = False
    for line in lines:
        if line.strip().startswith("OPENAI_API_KEY="):
            f.write(f"OPENAI_API_KEY={new_key}\n")
            updated = True
        else:
            f.write(line)

    if not updated:
        # Add key if it wasn't in the file
        f.write(f"\nOPENAI_API_KEY={new_key}\n")

print("✓ .env file updated!")
print()

# Verify settings can load
print("Verifying configuration...")
try:
    from app.config import settings
    # Force reload
    import importlib
    import app.config
    importlib.reload(app.config)
    from app.config import settings

    print(f"✓ Configuration loaded successfully")
    print(f"✓ Using model: {settings.openai_model}")
    print(f"✓ Using embeddings: {settings.openai_embedding_model}")
except Exception as e:
    print(f"⚠️ Warning: Could not load config: {e}")
    print("You may need to restart your terminal")

print()
print("=" * 60)
print("✓ Setup Complete!")
print("=" * 60)
print()
print("Next steps:")
print()
print("1. Restart your terminal (to reload environment)")
print()
print("2. Reactivate virtual environment:")
print("   venv\\Scripts\\activate")
print()
print("3. Try ingestion again:")
print("   python scripts\\ingest_cli.py --tenant bank-asia kb\\sample_channels.md")
print()
print("=" * 60)
