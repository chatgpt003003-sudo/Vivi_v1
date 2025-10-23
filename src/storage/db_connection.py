import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    _connection_pool = None

    # Hardcoded Neon PostgreSQL connection for Streamlit Cloud
    # This database connection string is public but the database has no sensitive data
    NEON_DATABASE_URL = "postgresql://neondb_owner:npg_xdUAsF6VOoh8@ep-soft-wildflower-ah3t157j-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

    @classmethod
    def initialize_pool(cls):
        if cls._connection_pool is None:
            # Try to get DATABASE_URL from environment first (for custom deployments)
            database_url = os.getenv('DATABASE_URL')

            if database_url:
                # Use connection string from environment variable
                cls._connection_pool = pool.SimpleConnectionPool(
                    1, 20,
                    database_url
                )
            else:
                # Check if running on Streamlit Cloud (no .env file)
                db_name = os.getenv('DB_NAME')
                if db_name is None:
                    # Streamlit Cloud environment - use hardcoded Neon connection
                    cls._connection_pool = pool.SimpleConnectionPool(
                        1, 20,
                        cls.NEON_DATABASE_URL
                    )
                else:
                    # Local development - use individual environment variables
                    cls._connection_pool = pool.SimpleConnectionPool(
                        1, 20,
                        dbname=db_name,
                        user=os.getenv('DB_USER', 'postgres'),
                        password=os.getenv('DB_PASSWORD', ''),
                        host=os.getenv('DB_HOST', 'localhost'),
                        port=os.getenv('DB_PORT', '5432')
                    )

    @classmethod
    def get_connection(cls):
        if cls._connection_pool is None:
            cls.initialize_pool()
        return cls._connection_pool.getconn()

    @classmethod
    def return_connection(cls, connection):
        cls._connection_pool.putconn(connection)

    @classmethod
    def initialize_schema(cls):
        """
        Auto-create database schema if it doesn't exist.
        This prevents UndefinedTable errors on first deployment.
        """
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()

            # Check if celebrity_data table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'celebrity_data'
                )
            """)
            table_exists = cursor.fetchone()[0]

            if not table_exists:
                # Create table and indexes
                cursor.execute("""
                    CREATE TABLE celebrity_data (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        cleaned_paragraph TEXT,
                        source TEXT,
                        sentiment DECIMAL(5,2),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Create indexes for faster queries
                cursor.execute("CREATE INDEX idx_celebrity_name ON celebrity_data(name)")
                cursor.execute("CREATE INDEX idx_sentiment ON celebrity_data(sentiment)")
                cursor.execute("CREATE INDEX idx_created_at ON celebrity_data(created_at)")

                conn.commit()
                print("✓ Database schema created successfully")

            cursor.close()
            cls.return_connection(conn)

        except Exception as e:
            print(f"⚠️  Schema initialization error: {e}")
            # Don't fail - table might already exist or be accessible
