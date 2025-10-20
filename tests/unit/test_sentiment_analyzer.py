#!/usr/bin/env python
"""
Test script for Sentiment Analyzer
Tests Google Gemini API sentiment analysis functionality
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data_processing.sentiment_analyzer import SentimentAnalyzer

def test_sentiment_analyzer():
    print("=" * 60)
    print("Testing Sentiment Analyzer (Google Gemini API)")
    print("=" * 60)

    analyzer = SentimentAnalyzer()

    # Test cases with expected sentiment categories
    test_cases = [
        ("周杰倫的新專輯非常棒，粉絲都很喜歡！演唱會門票立即售罄，展現其超高人氣。", "positive"),
        ("演唱會突然取消，粉絲感到非常失望和憤怒。主辦方的處理方式讓人不滿。", "negative"),
        ("周杰倫今天發布新專輯，包含10首歌曲。", "neutral"),
        ("這次的表演非常精彩，舞台效果震撼人心，觀眾反應熱烈！", "positive"),
        ("音質很差，表演水準也不如預期，真的很糟糕。", "negative"),
    ]

    print("\nTest 1: Basic sentiment analysis...")
    print()

    results = []
    for text, expected in test_cases:
        score = analyzer.analyze_sentiment(text)
        classification = analyzer.classify_sentiment(score)

        print(f"Text: {text[:50]}...")
        print(f"Score: {score:.2f}")
        print(f"Classification: {classification}")
        print(f"Expected: {expected}")

        # Verify score is in valid range
        assert -1.0 <= score <= 1.0, f"Score {score} out of range"

        # Store result
        results.append({
            'text': text,
            'score': score,
            'classification': classification,
            'expected': expected,
            'match': classification == expected
        })

        print()

    # Calculate accuracy
    matches = sum(1 for r in results if r['match'])
    accuracy = matches / len(results) * 100

    print(f"✓ Accuracy: {matches}/{len(results)} ({accuracy:.0f}%)")

    # Test 2: Sentiment with explanation
    print("\nTest 2: Sentiment analysis with explanation...")
    test_text = "周杰倫的演唱會非常成功，粉絲反應熱烈，門票銷售一空。"

    score, explanation = analyzer.analyze_with_explanation(test_text)

    print(f"\nText: {test_text}")
    print(f"Score: {score:.2f}")
    print(f"Explanation: {explanation}")

    assert -1.0 <= score <= 1.0, "Score out of range"
    assert len(explanation) > 0, "Explanation should not be empty"

    print("\n✓ Sentiment analysis with explanation successful")

    return True

if __name__ == "__main__":
    try:
        print()
        success = test_sentiment_analyzer()

        print("\n" + "=" * 60)
        if success:
            print("✓ SENTIMENT ANALYZER TEST PASSED")
            print("=" * 60)
            print("\nNote: Sentiment analysis accuracy may vary.")
            print("The model should generally identify positive/negative correctly.")
            sys.exit(0)
        else:
            print("✗ SENTIMENT ANALYZER TEST FAILED")
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
