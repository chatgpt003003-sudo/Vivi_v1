#!/usr/bin/env python
"""
Test script for Celebrity Manager
Validates celebrity list and checks mention thresholds
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data_collection.celebrity_manager import CelebrityManager

def test_celebrity_manager():
    print("=" * 60)
    print("Testing Celebrity Manager")
    print("=" * 60)

    # Test with a small sample
    test_celebrities = [
        "周杰倫",  # Jay Chou - should pass
        "蔡依林",  # Jolin Tsai - should pass
        "林志玲",  # Lin Chi-ling - should pass
        "Unknown Person XYZ123"  # Should fail
    ]

    manager = CelebrityManager(mention_threshold=50)

    print(f"\nValidating {len(test_celebrities)} test celebrities...")
    print(f"Mention threshold: {manager.mention_threshold:,}")
    print()

    validated = manager.validate_batch(test_celebrities)

    print()
    print("=" * 60)
    print(f"✓ Validation Results: {len(validated)}/{len(test_celebrities)} passed")
    print("=" * 60)

    for celeb in validated:
        print(f"  ✓ {celeb['name']}: {celeb['mention_count']:,} mentions")

    if len(validated) >= 2:
        print("\n✓ CELEBRITY MANAGER TEST PASSED")
        return True
    else:
        print("\n✗ TEST FAILED: Not enough celebrities validated")
        return False

def test_load_seed_list():
    print("\n" + "=" * 60)
    print("Testing Celebrity Seed List")
    print("=" * 60)

    try:
        celebrities = CelebrityManager.load_from_json('config/celebrity_seed_list.json')
        print(f"\n✓ Loaded {len(celebrities)} celebrities from seed list")

        # Show sample
        print("\nSample celebrities:")
        for i, celeb in enumerate(celebrities[:5], 1):
            name = celeb if isinstance(celeb, str) else celeb.get('name')
            category = celeb.get('category', 'N/A') if isinstance(celeb, dict) else 'N/A'
            print(f"  {i}. {name} ({category})")

        print(f"\n✓ SEED LIST TEST PASSED ({len(celebrities)} celebrities)")
        return True
    except Exception as e:
        print(f"\n✗ Failed to load seed list: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        # Test 1: Celebrity Manager
        result1 = test_celebrity_manager()

        # Test 2: Seed List
        result2 = test_load_seed_list()

        print("\n" + "=" * 60)
        if result1 and result2:
            print("✓ ALL TESTS PASSED")
            print("=" * 60)
            sys.exit(0)
        else:
            print("✗ SOME TESTS FAILED")
            print("=" * 60)
            sys.exit(1)

    except Exception as e:
        print(f"\n✗ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
