"""Offline evaluation script for intent detection."""

import json
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.intent import intent_detection_service


def load_eval_data(file_path: str) -> list[dict[str, Any]]:
    """Load evaluation dataset from JSONL file."""
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def evaluate_intent_detection(eval_data: list[dict[str, Any]]) -> dict[str, Any]:
    """Evaluate intent detection performance."""
    total = len(eval_data)
    correct_intents = 0
    ood_correct = 0
    ood_total = 0

    results = []

    for item in eval_data:
        utterance = item["utterance"]
        expected_intent = item["expected_intent"]

        # Detect intent
        result = intent_detection_service.detect_intent(
            utterance=utterance,
            channel="web",
            locale="en-IN",
            trace_id="eval",
        )

        predicted_intent = result.intent
        confidence = result.confidence

        # Check if correct
        is_correct = predicted_intent == expected_intent
        if is_correct:
            correct_intents += 1

        # Track OOD separately
        if expected_intent == "ood":
            ood_total += 1
            if predicted_intent == "ood" or result.ood:
                ood_correct += 1

        results.append({
            "utterance": utterance,
            "expected": expected_intent,
            "predicted": predicted_intent,
            "confidence": confidence,
            "correct": is_correct,
        })

    # Calculate metrics
    accuracy = correct_intents / total if total > 0 else 0.0
    ood_accuracy = ood_correct / ood_total if ood_total > 0 else 0.0

    return {
        "total_samples": total,
        "correct_predictions": correct_intents,
        "accuracy": accuracy,
        "ood_samples": ood_total,
        "ood_correct": ood_correct,
        "ood_accuracy": ood_accuracy,
        "results": results,
    }


def print_evaluation_report(eval_results: dict[str, Any]) -> None:
    """Print evaluation report."""
    print("\n" + "=" * 60)
    print("INTENT DETECTION EVALUATION REPORT")
    print("=" * 60)
    print(f"\nTotal Samples: {eval_results['total_samples']}")
    print(f"Correct Predictions: {eval_results['correct_predictions']}")
    print(f"Overall Accuracy: {eval_results['accuracy']:.2%}")
    print(f"\nOOD Samples: {eval_results['ood_samples']}")
    print(f"OOD Correct: {eval_results['ood_correct']}")
    print(f"OOD Accuracy: {eval_results['ood_accuracy']:.2%}")

    # Show errors
    print("\n" + "-" * 60)
    print("INCORRECT PREDICTIONS:")
    print("-" * 60)

    errors = [r for r in eval_results["results"] if not r["correct"]]
    for error in errors:
        print(f"\nUtterance: {error['utterance']}")
        print(f"Expected: {error['expected']}")
        print(f"Predicted: {error['predicted']} (confidence: {error['confidence']:.2f})")

    print("\n" + "=" * 60)


def main() -> None:
    """Run evaluation."""
    print("Loading evaluation dataset...")

    eval_file = Path(__file__).parent / "offline.jsonl"
    eval_data = load_eval_data(str(eval_file))

    print(f"Loaded {len(eval_data)} samples")
    print("\nRunning evaluation...")

    eval_results = evaluate_intent_detection(eval_data)

    print_evaluation_report(eval_results)

    # Save results
    output_file = Path(__file__).parent / "eval_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
