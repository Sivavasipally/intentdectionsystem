"""Interactive CLI for testing the intent detection system."""

import sys
from pathlib import Path
import requests
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


BASE_URL = "http://localhost:8000"


def print_header(text: str) -> None:
    """Print section header."""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def print_json(data: dict) -> None:
    """Pretty print JSON."""
    print(json.dumps(data, indent=2))


def test_health() -> bool:
    """Test health endpoint."""
    print_header("Testing Health Endpoint")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print_json(response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_intent_detection(utterance: str, tenant: str = "bank-asia") -> dict | None:
    """Test intent detection."""
    print_header(f"Testing Intent Detection")
    print(f"Utterance: {utterance}")

    try:
        response = requests.post(
            f"{BASE_URL}/intent/v1/detect",
            json={
                "utterance": utterance,
                "channel": "web",
                "locale": "en-IN",
                "tenant": tenant,
            },
            timeout=10,
        )

        print(f"\nStatus: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("\nResult:")
            print(f"  Intent: {data.get('intent')}")
            print(f"  Confidence: {data.get('confidence'):.2f}")
            print(f"  OOD: {data.get('ood')}")
            print(f"  Entities: {data.get('entities')}")
            print(f"  Trace ID: {data.get('traceId')}")
            return data
        else:
            print(f"Error: {response.text}")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None


def test_understand_and_open(utterance: str, tenant: str = "bank-asia") -> dict | None:
    """Test understand-and-open workflow."""
    print_header(f"Testing Understand-and-Open Workflow")
    print(f"Utterance: {utterance}")

    try:
        response = requests.post(
            f"{BASE_URL}/intent/v1/understand-and-open",
            json={
                "utterance": utterance,
                "tenant": tenant,
                "defaults": {"status": "active"},
            },
            timeout=15,
        )

        print(f"\nStatus: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("\nResult:")
            print(f"  Intent: {data.get('intent')}")
            print(f"  Confidence: {data.get('confidence'):.2f}")
            print(f"  Validated: {data.get('validated_from_kb')}")
            print(f"  Entities: {data.get('entities')}")

            citations = data.get('citations', [])
            if citations:
                print(f"\n  Citations ({len(citations)}):")
                for i, cit in enumerate(citations[:3], 1):
                    print(f"    {i}. {cit.get('doc')} (page {cit.get('page', 'N/A')})")
                    print(f"       {cit.get('snippet', '')[:80]}...")

            channel = data.get('channel_record')
            if channel:
                print(f"\n  Channel Created:")
                print(f"    ID: {channel.get('id')}")
                print(f"    Name: {channel.get('name')}")
                print(f"    Status: {channel.get('status')}")

            error = data.get('error')
            if error:
                print(f"\n  Error: {error}")

            print(f"\n  Trace ID: {data.get('traceId')}")
            return data
        else:
            print(f"Error: {response.text}")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None


def test_simulate() -> None:
    """Test simulate endpoint with multiple utterances."""
    print_header("Testing Simulate Endpoint")

    utterances = [
        "Open WhatsApp channel for Retail Banking",
        "What are NEFT transfer charges?",
        "Block my credit card",
        "What's the weather today?",
    ]

    try:
        response = requests.post(
            f"{BASE_URL}/intent/v1/simulate",
            json={
                "utterances": utterances,
                "tenant": "bank-asia",
            },
            timeout=30,
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])

            print(f"\nResults ({len(results)} utterances):\n")

            for i, result in enumerate(results, 1):
                print(f"{i}. \"{result.get('utterance')}\"")
                if 'error' in result:
                    print(f"   Error: {result.get('error')}")
                else:
                    print(f"   Intent: {result.get('intent')}")
                    print(f"   Confidence: {result.get('confidence', 0):.2f}")
                    print(f"   OOD: {result.get('ood')}")
                print()

        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Error: {e}")


def get_channel(channel_id: str) -> None:
    """Get channel details."""
    print_header(f"Getting Channel: {channel_id}")

    try:
        response = requests.get(f"{BASE_URL}/channels/{channel_id}", timeout=5)

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("\nChannel Details:")
            print(f"  ID: {data.get('id')}")
            print(f"  Name: {data.get('name')}")
            print(f"  Type: {data.get('channel_type')}")
            print(f"  Department: {data.get('department')}")
            print(f"  Status: {data.get('status')}")
            print(f"  Created: {data.get('created_at')}")
            print(f"  Tenant: {data.get('tenant')}")

            details = data.get('details', [])
            if details:
                print(f"\n  Details ({len(details)}):")
                for detail in details:
                    print(f"    {detail.get('key')}: {detail.get('value')}")
                    if detail.get('citation'):
                        print(f"      Source: {detail.get('citation')}")

        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Error: {e}")


def list_channels(tenant: str = "bank-asia") -> None:
    """List all channels."""
    print_header("Listing Channels")

    try:
        response = requests.get(
            f"{BASE_URL}/channels/",
            params={"tenant": tenant, "limit": 10},
            timeout=5,
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            channels = response.json()
            print(f"\nFound {len(channels)} channel(s):\n")

            for channel in channels:
                print(f"  {channel.get('id')}")
                print(f"    Name: {channel.get('name')}")
                print(f"    Type: {channel.get('channel_type')}")
                print(f"    Status: {channel.get('status')}")
                print()

        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Error: {e}")


def interactive_mode() -> None:
    """Interactive testing mode."""
    print_header("Interactive Testing Mode")
    print("Type 'help' for commands, 'quit' to exit")

    while True:
        try:
            command = input("\n> ").strip()

            if not command:
                continue

            if command.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            elif command.lower() == "help":
                print("\nAvailable commands:")
                print("  detect <utterance>     - Detect intent")
                print("  open <utterance>       - Full workflow")
                print("  simulate               - Test multiple utterances")
                print("  list                   - List channels")
                print("  get <channel_id>       - Get channel details")
                print("  health                 - Health check")
                print("  quit                   - Exit")

            elif command.lower() == "health":
                test_health()

            elif command.lower().startswith("detect "):
                utterance = command[7:].strip()
                if utterance:
                    test_intent_detection(utterance)
                else:
                    print("Usage: detect <utterance>")

            elif command.lower().startswith("open "):
                utterance = command[5:].strip()
                if utterance:
                    test_understand_and_open(utterance)
                else:
                    print("Usage: open <utterance>")

            elif command.lower() == "simulate":
                test_simulate()

            elif command.lower() == "list":
                list_channels()

            elif command.lower().startswith("get "):
                channel_id = command[4:].strip()
                if channel_id:
                    get_channel(channel_id)
                else:
                    print("Usage: get <channel_id>")

            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def run_smoke_tests() -> None:
    """Run smoke tests."""
    print_header("Running Smoke Tests")

    results = []

    # Test 1: Health check
    print("\n1. Health Check")
    results.append(("Health", test_health()))

    # Test 2: Intent detection
    print("\n2. Intent Detection")
    result = test_intent_detection("What are NEFT charges?")
    results.append(("Intent Detection", result is not None))

    # Test 3: Understand and open
    print("\n3. Understand and Open")
    result = test_understand_and_open("Open WhatsApp channel for retail banking")
    results.append(("Understand and Open", result is not None))

    # Summary
    print_header("Smoke Test Results")
    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {name}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("✓ All smoke tests passed!")
    else:
        print(f"✗ {total - passed} test(s) failed")


def main() -> None:
    """Main entry point."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "smoke":
            run_smoke_tests()
        elif command == "health":
            test_health()
        elif command == "detect" and len(sys.argv) > 2:
            utterance = " ".join(sys.argv[2:])
            test_intent_detection(utterance)
        elif command == "open" and len(sys.argv) > 2:
            utterance = " ".join(sys.argv[2:])
            test_understand_and_open(utterance)
        elif command == "simulate":
            test_simulate()
        elif command == "list":
            list_channels()
        elif command == "get" and len(sys.argv) > 2:
            get_channel(sys.argv[2])
        else:
            print("Usage:")
            print("  python scripts/test_system.py smoke")
            print("  python scripts/test_system.py health")
            print("  python scripts/test_system.py detect <utterance>")
            print("  python scripts/test_system.py open <utterance>")
            print("  python scripts/test_system.py simulate")
            print("  python scripts/test_system.py list")
            print("  python scripts/test_system.py get <channel_id>")
            print("\nOr run without arguments for interactive mode")
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
