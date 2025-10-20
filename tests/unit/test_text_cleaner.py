#!/usr/bin/env python
"""
Test script for Text Cleaner module
Tests Google Gemini API text cleaning functionality
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data_processing.text_cleaner import TextCleaner

def test_text_cleaner():
    print("=" * 60)
    print("Testing Text Cleaner (Google Gemini API)")
    print("=" * 60)

    cleaner = TextCleaner()

    # Test data - simulated search results
    test_results = [
        {
            'title': '周杰倫新專輯發布',
            'snippet': '歌手周杰倫今天發布新專輯，受到粉絲熱烈歡迎。這張專輯包含10首全新歌曲，展現了他獨特的音樂風格。',
            'link': 'https://example.com/1'
        },
        {
            'title': '周杰倫演唱會門票秒殺',
            'snippet': '演唱會門票在開賣後立即售罄，顯示其超高人氣。許多歌迷在社交媒體上分享他們的興奮心情。',
            'link': 'https://example.com/2'
        },
        {
            'title': '周杰倫獲音樂大獎',
            'snippet': '在昨晚的音樂頒獎典禮上，周杰倫獲得最佳男歌手獎，這是他第15次獲得此殊榮。',
            'link': 'https://example.com/3'
        }
    ]

    print("\nTest 1: Clean search results...")
    print(f"Input: {len(test_results)} search results")

    cleaned = cleaner.clean_search_results(test_results)

    print(f"\n✓ Cleaned text ({len(cleaned)} chars):")
    print("-" * 60)
    print(cleaned)
    print("-" * 60)

    assert len(cleaned) > 0, "Cleaned text should not be empty"
    assert len(cleaned) <= 600, "Cleaned text should be summarized"

    print("\n✓ Text cleaning successful")

    # Test 2: Extract key points
    print("\nTest 2: Extract key points...")

    key_points = cleaner.extract_key_points(cleaned)

    print(f"\n✓ Key points extracted: {len(key_points)}")
    for i, point in enumerate(key_points, 1):
        print(f"  {i}. {point}")

    assert len(key_points) > 0, "Should extract at least one key point"

    print("\n✓ Key point extraction successful")

    # Test 3: Simple text cleaning (no API)
    print("\nTest 3: Simple text cleaning...")

    test_text = "這是一個測試   文字    點擊訂閱    廣告"
    simple_cleaned = cleaner.clean_text_simple(test_text)

    print(f"Original: '{test_text}'")
    print(f"Cleaned: '{simple_cleaned}'")

    assert "  " not in simple_cleaned, "Should remove extra whitespace"
    print("\n✓ Simple cleaning successful")

    return True

if __name__ == "__main__":
    try:
        print()
        success = test_text_cleaner()

        print("\n" + "=" * 60)
        if success:
            print("✓ TEXT CLEANER TEST PASSED")
            print("=" * 60)
            sys.exit(0)
        else:
            print("✗ TEXT CLEANER TEST FAILED")
            print("=" * 60)
            sys.exit(1)

    except Exception as e:
        print(f"\n✗ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\nPlease check:")
        print("1. GEMINI_API_KEY is valid")
        print("2. API quota is not exceeded")
        print("3. Internet connection is working")
        sys.exit(1)
