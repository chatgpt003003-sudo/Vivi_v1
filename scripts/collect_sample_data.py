#!/usr/bin/env python
"""
Quick script to collect sample data for UI testing
Processes a small batch of celebrities
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_processing.pipeline import DataPipeline
from src.data_collection.celebrity_manager import CelebrityManager

def main():
    print("=" * 60)
    print("Collecting Sample Data for UI Testing")
    print("=" * 60)

    pipeline = DataPipeline()

    # Load celebrity list
    print("\nLoading celebrity list...")
    celebrities = CelebrityManager.load_from_json('config/celebrity_seed_list.json')
    print(f"✓ Loaded {len(celebrities)} celebrities")

    # Process a sample batch
    sample_size = 100
    print(f"\nProcessing {sample_size} celebrities...")
    print("Using parallel processing for faster data collection...\n")
    print("With parallel processing (4-8 workers):")
    print("  Estimated time: 3-5 minutes (vs 15-30 minutes sequential)\n")

    summary = pipeline.process_multiple_celebrities(
        celebrities,
        limit=sample_size,
        use_parallel=True  # Enable parallel processing
    )

    print("\n" + "=" * 60)
    print("Sample Data Collection Complete")
    print("=" * 60)

    print(f"\nResults:")
    print(f"  Total attempted: {summary['total_attempted']}")
    print(f"  Successful: {summary['successful']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Success rate: {summary['success_rate']:.1f}%")

    if summary['successful'] > 0:
        print(f"\n✓ Successfully processed celebrities:")
        for celeb in summary['processed']:
            sentiment_label = "Positive" if celeb['sentiment'] > 0.3 else "Negative" if celeb['sentiment'] < -0.3 else "Neutral"
            print(f"  - {celeb['name']}: {celeb['sentiment']:.2f} ({sentiment_label})")

    if summary['failed'] > 0:
        print(f"\n✗ Failed celebrities: {', '.join(summary['failed_names'])}")

    print("\n" + "=" * 60)
    print("You can now launch the UI:")
    print("  venv/bin/streamlit run src/ui/app.py")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
