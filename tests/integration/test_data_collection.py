#!/usr/bin/env python
"""
Integration test for data collection
Tests the complete flow: Search -> Store to Database
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data_collection.google_search import GoogleSearchCollector
from src.data_collection.celebrity_manager import CelebrityManager
from src.storage.db_connection import DatabaseConnection
from datetime import datetime

def test_data_collection_flow():
    print("=" * 60)
    print("Integration Test: Data Collection Flow")
    print("=" * 60)

    # Step 1: Initialize collector
    print("\n[Step 1] Initializing Google Search Collector...")
    collector = GoogleSearchCollector()
    print("✓ Collector initialized")

    # Step 2: Search for a celebrity
    test_celebrity = "周杰倫"
    print(f"\n[Step 2] Searching for '{test_celebrity}'...")
    search_results = collector.search_celebrity(test_celebrity, num_results=3)
    print(f"✓ Found {len(search_results)} results")

    if not search_results:
        print("✗ No search results - cannot proceed with test")
        return False

    # Step 3: Prepare data for database
    print(f"\n[Step 3] Preparing data for database...")

    # Combine search results into a single text
    combined_text = "\n\n".join([
        f"Title: {result['title']}\nSnippet: {result['snippet']}\nLink: {result['link']}"
        for result in search_results
    ])

    # For now, we'll store raw data (sentiment analysis in Part 3)
    data_entry = {
        'name': test_celebrity,
        'cleaned_paragraph': combined_text[:500],  # Limit to 500 chars for now
        'source': search_results[0]['link'] if search_results else None,
        'sentiment': 0.0  # Placeholder - will be calculated in Part 3
    }

    print(f"✓ Data prepared:")
    print(f"  Name: {data_entry['name']}")
    print(f"  Text length: {len(data_entry['cleaned_paragraph'])} chars")
    print(f"  Source: {data_entry['source'][:50]}...")

    # Step 4: Store to database
    print(f"\n[Step 4] Storing to database...")
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO celebrity_data (name, cleaned_paragraph, source, sentiment)
            VALUES (%s, %s, %s, %s)
            RETURNING id, created_at
        """, (
            data_entry['name'],
            data_entry['cleaned_paragraph'],
            data_entry['source'],
            data_entry['sentiment']
        ))

        result = cursor.fetchone()
        record_id, created_at = result
        conn.commit()

        print(f"✓ Data stored successfully")
        print(f"  Record ID: {record_id}")
        print(f"  Created at: {created_at}")

    except Exception as e:
        conn.rollback()
        print(f"✗ Database error: {str(e)}")
        cursor.close()
        DatabaseConnection.return_connection(conn)
        return False
    finally:
        cursor.close()
        DatabaseConnection.return_connection(conn)

    # Step 5: Verify data retrieval
    print(f"\n[Step 5] Verifying data retrieval...")
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, sentiment, created_at
        FROM celebrity_data
        WHERE name = %s
        ORDER BY created_at DESC
        LIMIT 1
    """, (test_celebrity,))

    retrieved = cursor.fetchone()

    if retrieved:
        print(f"✓ Data retrieved successfully:")
        print(f"  ID: {retrieved[0]}")
        print(f"  Name: {retrieved[1]}")
        print(f"  Sentiment: {retrieved[2]}")
        print(f"  Date: {retrieved[3]}")
    else:
        print(f"✗ Could not retrieve data")
        cursor.close()
        DatabaseConnection.return_connection(conn)
        return False

    cursor.close()
    DatabaseConnection.return_connection(conn)

    return True

if __name__ == "__main__":
    try:
        print()
        success = test_data_collection_flow()

        print("\n" + "=" * 60)
        if success:
            print("✓ INTEGRATION TEST PASSED")
            print("=" * 60)
            print("\nData collection flow is working!")
            print("Ready for Part 3: Data Processing (Text Cleaning & Sentiment)")
            sys.exit(0)
        else:
            print("✗ INTEGRATION TEST FAILED")
            print("=" * 60)
            sys.exit(1)

    except Exception as e:
        print(f"\n✗ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
