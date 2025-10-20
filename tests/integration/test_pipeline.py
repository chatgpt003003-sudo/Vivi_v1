#!/usr/bin/env python
"""
Integration test for complete data processing pipeline
Tests: Search → Clean → Sentiment → Database
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data_processing.pipeline import DataPipeline
from src.storage.db_connection import DatabaseConnection

def test_single_celebrity_pipeline():
    print("=" * 60)
    print("Integration Test: Complete Data Processing Pipeline")
    print("=" * 60)

    pipeline = DataPipeline()

    # Test with a well-known Taiwan celebrity
    test_celebrity = "周杰倫"

    print(f"\n[Test 1] Processing single celebrity: {test_celebrity}")
    print("Steps: Search → Clean → Sentiment → Database")
    print()

    result = pipeline.process_celebrity(test_celebrity, num_results=5)

    if result:
        print("\n✓ Processing successful!")
        print(f"  Record ID: {result['record_id']}")
        print(f"  Name: {result['name']}")
        print(f"  Sentiment: {result['sentiment']:.2f}")
        print(f"  Mentions: {result['mention_count']}")
        print(f"  Text preview: {result['cleaned_text'][:100]}...")
        print(f"  Source: {result['source'][:60]}...")
    else:
        print("\n✗ Processing failed")
        return False

    return True

def test_multiple_celebrities_pipeline():
    print("\n" + "=" * 60)
    print("[Test 2] Processing multiple celebrities")
    print("=" * 60)

    pipeline = DataPipeline()

    # Test with a small batch
    test_celebrities = ["蔡依林", "林志玲", "林書豪"]

    print(f"\nProcessing {len(test_celebrities)} celebrities...")
    print()

    summary = pipeline.process_multiple_celebrities(test_celebrities, limit=3)

    print("\n✓ Batch processing complete!")
    print(f"  Total attempted: {summary['total_attempted']}")
    print(f"  Successful: {summary['successful']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Success rate: {summary['success_rate']:.1f}%")

    if summary['successful'] > 0:
        print("\n  Processed celebrities:")
        for celeb in summary['processed']:
            print(f"    - {celeb['name']}: sentiment={celeb['sentiment']:.2f}")

    if summary['failed'] > 0:
        print("\n  Failed celebrities:")
        for name in summary['failed_names']:
            print(f"    - {name}")

    return summary['successful'] >= 2

def test_data_retrieval():
    print("\n" + "=" * 60)
    print("[Test 3] Data retrieval from database")
    print("=" * 60)

    pipeline = DataPipeline()

    recent_data = pipeline.get_recent_data(limit=5)

    print(f"\n✓ Retrieved {len(recent_data)} recent records:")
    print()

    for i, record in enumerate(recent_data, 1):
        print(f"{i}. {record['name']}")
        print(f"   Sentiment: {record['sentiment']:.2f}")
        print(f"   Date: {record['created_at']}")
        print(f"   Preview: {record['text_preview']}...")
        print()

    return len(recent_data) > 0

def verify_database_stats():
    print("=" * 60)
    print("[Test 4] Database statistics")
    print("=" * 60)

    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor()

    # Total records
    cursor.execute("SELECT COUNT(*) FROM celebrity_data;")
    total = cursor.fetchone()[0]

    # Sentiment distribution
    cursor.execute("""
        SELECT
            COUNT(CASE WHEN sentiment > 0.3 THEN 1 END) as positive,
            COUNT(CASE WHEN sentiment BETWEEN -0.3 AND 0.3 THEN 1 END) as neutral,
            COUNT(CASE WHEN sentiment < -0.3 THEN 1 END) as negative,
            AVG(sentiment) as avg_sentiment
        FROM celebrity_data;
    """)

    pos, neu, neg, avg = cursor.fetchone()

    # Unique celebrities
    cursor.execute("SELECT COUNT(DISTINCT name) FROM celebrity_data;")
    unique = cursor.fetchone()[0]

    cursor.close()
    DatabaseConnection.return_connection(conn)

    print(f"\n✓ Database Statistics:")
    print(f"  Total records: {total}")
    print(f"  Unique celebrities: {unique}")
    print(f"  Average sentiment: {float(avg):.2f}")
    print(f"  Sentiment distribution:")
    print(f"    Positive: {pos} ({pos/total*100:.1f}%)")
    print(f"    Neutral: {neu} ({neu/total*100:.1f}%)")
    print(f"    Negative: {neg} ({neg/total*100:.1f}%)")

    return total > 0

if __name__ == "__main__":
    try:
        print()

        # Run all tests
        test1 = test_single_celebrity_pipeline()
        test2 = test_multiple_celebrities_pipeline()
        test3 = test_data_retrieval()
        test4 = verify_database_stats()

        print("\n" + "=" * 60)
        if test1 and test2 and test3 and test4:
            print("✓ ALL PIPELINE TESTS PASSED")
            print("=" * 60)
            print("\nComplete data processing pipeline is working!")
            print("Ready for Part 4: Desktop UI")
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
