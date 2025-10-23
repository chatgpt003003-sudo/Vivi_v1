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
