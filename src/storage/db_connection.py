import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    _connection_pool = None

    @classmethod
    def initialize_pool(cls):
        if cls._connection_pool is None:
            # Try to get DATABASE_URL first (for cloud deployment)
            database_url = os.getenv('DATABASE_URL')

            if database_url:
                # Use connection string for cloud (Neon, Render, etc.)
                cls._connection_pool = pool.SimpleConnectionPool(
                    1, 20,
                    database_url
                )
            else:
                # Fall back to individual environment variables for local dev
                cls._connection_pool = pool.SimpleConnectionPool(
                    1, 20,
                    dbname=os.getenv('DB_NAME', 'celebrity_index'),
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
