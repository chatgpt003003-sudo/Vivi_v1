#!/usr/bin/env python
"""
Test script to verify database connection and schema setup
Run this after PostgreSQL is installed and configured
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.storage.db_connection import DatabaseConnection

def test_database_connection():
    print("Testing database connection...")
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        # Test connection
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✓ PostgreSQL version: {version[0]}")

        # Check if table exists
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'celebrity_data';
        """)

        result = cursor.fetchone()
        if result:
            print(f"✓ Table 'celebrity_data' exists")

            # Check table structure
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'celebrity_data'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            print("\n✓ Table structure:")
            for col_name, col_type in columns:
                print(f"  - {col_name}: {col_type}")
        else:
            print("✗ Table 'celebrity_data' not found")
            print("  Run: psql -U postgres -d celebrity_index -f src/storage/schema.sql")

        cursor.close()
        DatabaseConnection.return_connection(conn)

        print("\n✓ Database connection test passed")

    except Exception as e:
        print(f"✗ Database connection failed: {str(e)}")
        print("\nMake sure:")
        print("1. PostgreSQL is installed and running")
        print("2. Database 'celebrity_index' exists")
        print("3. Credentials in .env file are correct")
        sys.exit(1)

if __name__ == "__main__":
    test_database_connection()
