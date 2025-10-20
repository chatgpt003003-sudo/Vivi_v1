#!/bin/bash
# Database Setup Script for Celebrity Index Collector
# This script sets up the PostgreSQL database and applies the schema

echo "======================================"
echo "Celebrity Index Database Setup"
echo "======================================"
echo ""

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "✗ PostgreSQL is not installed"
    echo ""
    echo "Please install PostgreSQL first:"
    echo "  macOS: brew install postgresql@14"
    echo "  Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    echo ""
    exit 1
fi

echo "✓ PostgreSQL is installed"

# Check if PostgreSQL service is running
if ! pg_isready &> /dev/null; then
    echo "✗ PostgreSQL service is not running"
    echo ""
    echo "Please start PostgreSQL:"
    echo "  macOS: brew services start postgresql@14"
    echo "  Ubuntu: sudo service postgresql start"
    echo ""
    exit 1
fi

echo "✓ PostgreSQL service is running"
echo ""

# Create database
echo "Creating database 'celebrity_index'..."
psql -U postgres -c "CREATE DATABASE celebrity_index;" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ Database created successfully"
else
    echo "⚠ Database may already exist (this is okay)"
fi

# Apply schema
echo ""
echo "Applying database schema..."
psql -U postgres -d celebrity_index -f src/storage/schema.sql

if [ $? -eq 0 ]; then
    echo "✓ Schema applied successfully"
else
    echo "✗ Failed to apply schema"
    exit 1
fi

# Verify setup
echo ""
echo "Verifying database setup..."
psql -U postgres -d celebrity_index -c "\dt" | grep celebrity_data

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "✓ Database setup complete!"
    echo "======================================"
    echo ""
    echo "You can now:"
    echo "1. Update .env file with your database credentials"
    echo "2. Run: venv/bin/python tests/unit/test_db_connection.py"
    echo ""
else
    echo "✗ Table verification failed"
    exit 1
fi
