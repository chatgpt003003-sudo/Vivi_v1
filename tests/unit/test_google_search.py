#!/usr/bin/env python
"""
Test script for Google Search API integration
Run this to verify API credentials and search functionality
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data_collection.google_search import GoogleSearchCollector

def test_google_search():
    print("=" * 60)
    print("Testing Google Search API Integration")
    print("=" * 60)

    collector = GoogleSearchCollector()

    # Test with a well-known Taiwan celebrity
    test_celebrity = "周杰倫"  # Jay Chou
    print(f"\nTest 1: Searching for '{test_celebrity}'...")

    results = collector.search_celebrity(test_celebrity, num_results=5)

    print(f"✓ Results found: {len(results)}")

    if results:
        print(f"\n✓ Sample result:")
        print(f"  Title: {results[0]['title']}")
        print(f"  Snippet: {results[0]['snippet'][:100]}...")
        print(f"  Link: {results[0]['link']}")
        print(f"  Date: {results[0]['date']}")

        # Verify structure
        assert 'title' in results[0], "Missing 'title' field"
        assert 'snippet' in results[0], "Missing 'snippet' field"
        assert 'link' in results[0], "Missing 'link' field"
        print("\n✓ All required fields present")
    else:
        print("\n⚠ Warning: No results found")
        print("  This could mean:")
        print("  - API quota exceeded")
        print("  - Search Engine ID not configured correctly")
        print("  - No recent news about this celebrity")

    # Test mention count
    print(f"\nTest 2: Getting total mentions for '{test_celebrity}'...")
    mentions = collector.get_total_mentions(test_celebrity)
    print(f"✓ Total mentions: {mentions:,}")

    if mentions > 0:
        print("\n" + "=" * 60)
        print("✓ GOOGLE SEARCH API TEST PASSED")
        print("=" * 60)
        return True
    else:
        print("\n" + "=" * 60)
        print("⚠ WARNING: API working but no results")
        print("=" * 60)
        return False

if __name__ == "__main__":
    try:
        success = test_google_search()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        print("\nPlease check:")
        print("1. GOOGLE_API_KEY is valid")
        print("2. GOOGLE_SEARCH_ENGINE_ID is correct")
        print("3. Custom Search Engine has 'Search entire web' enabled")
        print("4. API quota is not exceeded")
        sys.exit(1)
