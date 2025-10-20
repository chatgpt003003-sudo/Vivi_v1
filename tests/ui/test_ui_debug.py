#!/usr/bin/env python
"""
UI Debug Test - Checks for common UI issues before launching
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.storage.db_connection import DatabaseConnection
import pandas as pd

def test_database_connectivity():
    """Test if database has data for UI"""
    print("=" * 60)
    print("UI Debug Test 1: Database Connectivity")
    print("=" * 60)

    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        # Check total records
        cursor.execute("SELECT COUNT(*) FROM celebrity_data;")
        total = cursor.fetchone()[0]
        print(f"\n✓ Total records in database: {total}")

        if total == 0:
            print("✗ ERROR: No data in database!")
            print("  Run: venv/bin/python scripts/collect_sample_data.py")
            return False

        # Check unique celebrities
        cursor.execute("SELECT COUNT(DISTINCT name) FROM celebrity_data;")
        unique = cursor.fetchone()[0]
        print(f"✓ Unique celebrities: {unique}")

        # Check for required columns
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'celebrity_data'
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        print(f"\n✓ Table structure:")
        for col_name, col_type in columns:
            print(f"  - {col_name}: {col_type}")

        required_cols = ['name', 'sentiment', 'created_at', 'cleaned_paragraph', 'source']
        col_names = [col[0] for col in columns]
        missing = [col for col in required_cols if col not in col_names]

        if missing:
            print(f"\n✗ ERROR: Missing required columns: {missing}")
            return False

        cursor.close()
        DatabaseConnection.return_connection(conn)

        return True

    except Exception as e:
        print(f"\n✗ Database error: {str(e)}")
        return False

def test_rankings_query():
    """Test the rankings view query"""
    print("\n" + "=" * 60)
    print("UI Debug Test 2: Rankings Query")
    print("=" * 60)

    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        # Test the rankings query used in UI
        query = """
            WITH ranked_data AS (
                SELECT
                    name,
                    sentiment,
                    created_at,
                    cleaned_paragraph,
                    source,
                    ROW_NUMBER() OVER (PARTITION BY name ORDER BY created_at DESC) as rn
                FROM celebrity_data
            )
            SELECT
                name,
                sentiment,
                created_at,
                cleaned_paragraph,
                source
            FROM ranked_data
            WHERE rn = 1
            ORDER BY sentiment DESC
            LIMIT 10
        """

        cursor.execute(query)
        results = cursor.fetchall()

        print(f"\n✓ Query executed successfully")
        print(f"✓ Retrieved {len(results)} records")

        if results:
            print(f"\nTop 3 celebrities:")
            for i, row in enumerate(results[:3], 1):
                print(f"  {i}. {row[0]}: {float(row[1]):.2f}")
        else:
            print("✗ WARNING: No results from rankings query")

        # Test conversion to DataFrame
        df = pd.DataFrame(results, columns=['Name', 'Sentiment Score', 'Date', 'Summary', 'Source'])
        print(f"\n✓ DataFrame created: {len(df)} rows, {len(df.columns)} columns")

        cursor.close()
        DatabaseConnection.return_connection(conn)

        return True

    except Exception as e:
        print(f"\n✗ Query error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_statistics_query():
    """Test the statistics query"""
    print("\n" + "=" * 60)
    print("UI Debug Test 3: Statistics Query")
    print("=" * 60)

    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        # Test statistics query
        cursor.execute("""
            SELECT
                COUNT(*) as total_records,
                COUNT(DISTINCT name) as unique_celebrities,
                AVG(sentiment) as avg_sentiment
            FROM celebrity_data
        """)
        total, unique, avg_sent = cursor.fetchone()

        print(f"\n✓ Statistics:")
        print(f"  Total records: {total}")
        print(f"  Unique celebrities: {unique}")
        print(f"  Average sentiment: {float(avg_sent):.2f}")

        # Test sentiment distribution
        cursor.execute("""
            SELECT
                COUNT(CASE WHEN sentiment > 0.3 THEN 1 END) as positive,
                COUNT(CASE WHEN sentiment BETWEEN -0.3 AND 0.3 THEN 1 END) as neutral,
                COUNT(CASE WHEN sentiment < -0.3 THEN 1 END) as negative
            FROM (
                SELECT DISTINCT ON (name) name, sentiment
                FROM celebrity_data
                ORDER BY name, created_at DESC
            ) latest
        """)
        pos, neu, neg = cursor.fetchone()

        print(f"\n✓ Sentiment distribution:")
        print(f"  Positive: {pos}")
        print(f"  Neutral: {neu}")
        print(f"  Negative: {neg}")

        cursor.close()
        DatabaseConnection.return_connection(conn)

        return True

    except Exception as e:
        print(f"\n✗ Statistics query error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_trend_query():
    """Test the trend query"""
    print("\n" + "=" * 60)
    print("UI Debug Test 4: Trend Query")
    print("=" * 60)

    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        # Get a celebrity name
        cursor.execute("SELECT DISTINCT name FROM celebrity_data LIMIT 1;")
        result = cursor.fetchone()

        if not result:
            print("✗ No celebrities in database")
            return False

        test_celeb = result[0]
        print(f"\nTesting trend query for: {test_celeb}")

        from datetime import datetime, timedelta
        start_date = datetime.now() - timedelta(days=7)

        query = """
            SELECT created_at, sentiment, cleaned_paragraph
            FROM celebrity_data
            WHERE name = %s
            AND created_at >= %s
            ORDER BY created_at ASC
        """

        cursor.execute(query, (test_celeb, start_date))
        results = cursor.fetchall()

        print(f"✓ Trend query executed successfully")
        print(f"✓ Retrieved {len(results)} historical records")

        if results:
            print(f"\nTrend data:")
            for row in results:
                print(f"  {row[0]}: {float(row[1]):.2f}")

        cursor.close()
        DatabaseConnection.return_connection(conn)

        return True

    except Exception as e:
        print(f"\n✗ Trend query error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_imports():
    """Test if UI dependencies can be imported"""
    print("\n" + "=" * 60)
    print("UI Debug Test 5: Import Dependencies")
    print("=" * 60)

    try:
        print("\nTesting imports...")

        import streamlit as st
        print("✓ streamlit imported")

        import plotly.express as px
        print("✓ plotly.express imported")

        import plotly.graph_objects as go
        print("✓ plotly.graph_objects imported")

        import pandas as pd
        print("✓ pandas imported")

        return True

    except ImportError as e:
        print(f"\n✗ Import error: {str(e)}")
        print("  Run: venv/bin/pip install streamlit plotly pandas")
        return False

def main():
    print("\n" + "=" * 60)
    print("CELEBRITY INDEX COLLECTOR - UI DEBUG TEST")
    print("=" * 60)
    print()

    tests = [
        ("Database Connectivity", test_database_connectivity),
        ("Rankings Query", test_rankings_query),
        ("Statistics Query", test_statistics_query),
        ("Trend Query", test_trend_query),
        ("UI Dependencies", test_ui_imports),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    passed = sum(1 for _, r in results if r)
    total = len(results)

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED - UI IS READY TO LAUNCH")
        print("=" * 60)
        print("\nTo launch the UI, run:")
        print("  ./scripts/run_ui.sh")
        print("  or")
        print("  venv/bin/streamlit run src/ui/app.py")
        return 0
    else:
        print("\n" + "=" * 60)
        print("✗ SOME TESTS FAILED - FIX ISSUES BEFORE LAUNCHING UI")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
