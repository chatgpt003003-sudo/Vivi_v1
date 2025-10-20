# Celebrity Index Collector - Setup Guide

## Part 1: Environment Setup & Configuration ✓

### Completed Steps

1. **Project Structure Created** ✓
   - Created directory structure: `src/`, `tests/`, `config/`, `logs/`
   - Initialized Python packages with `__init__.py` files

2. **Virtual Environment & Dependencies** ✓
   - Created virtual environment in `venv/`
   - Installed all required packages from `requirements.txt`
   - Verified package installation successful

3. **API Configuration Files** ✓
   - Created `.env` file (template - needs your API keys)
   - Created `config/api_config.py` for loading environment variables

4. **Database Schema** ✓
   - Created simplified schema with fields: name, cleaned_paragraph, source, sentiment
   - Schema file: `src/storage/schema.sql`
   - Database connection module: `src/storage/db_connection.py`

### Next Steps - PostgreSQL Setup

PostgreSQL is **NOT YET INSTALLED** on this system. Please complete the following:

#### 1. Install PostgreSQL

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
```

#### 2. Run Database Setup Script

```bash
./scripts/setup_database.sh
```

This script will:
- Create the `celebrity_index` database
- Apply the schema from `src/storage/schema.sql`
- Verify the setup

#### 3. Configure API Credentials

Edit `.env` file and add your actual API keys:

```
GOOGLE_API_KEY=your_actual_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_actual_search_engine_id
GEMINI_API_KEY=your_actual_gemini_api_key
DB_PASSWORD=your_postgres_password
```

**How to get API keys:**
- **Google Search API**: https://developers.google.com/custom-search/v1/introduction
- **Google Gemini API**: https://ai.google.dev/

#### 4. Verify Setup

Run the database connection test:

```bash
venv/bin/python tests/unit/test_db_connection.py
```

Expected output:
```
Testing database connection...
✓ PostgreSQL version: PostgreSQL 14.x...
✓ Table 'celebrity_data' exists

✓ Table structure:
  - id: integer
  - name: character varying
  - cleaned_paragraph: text
  - source: text
  - sentiment: numeric
  - created_at: timestamp without time zone

✓ Database connection test passed
```

### Project Structure

```
vivi/
├── .env                          # API credentials (configured)
├── requirements.txt              # Python dependencies (installed)
├── SETUP.md                      # This file
├── CLAUDE.md                     # Project instructions
├── config/
│   └── api_config.py            # API configuration loader ✓
├── src/
│   ├── data_collection/         # Future: Data collection modules
│   ├── data_processing/         # Future: Data processing pipeline
│   ├── storage/
│   │   ├── schema.sql           # Database schema ✓
│   │   └── db_connection.py     # Database connection pool ✓
│   └── ui/                      # Future: Desktop UI
├── tests/
│   ├── unit/
│   │   └── test_db_connection.py # DB connection test ✓
│   └── integration/             # Future: Integration tests
├── scripts/
│   └── setup_database.sh        # Database setup script ✓
├── logs/                        # Application logs
└── venv/                        # Virtual environment ✓
```

### Database Schema (Simplified)

```sql
celebrity_data (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    cleaned_paragraph TEXT,
    source TEXT,
    sentiment DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Fields:**
- `name`: Celebrity name
- `cleaned_paragraph`: Cleaned text from Gemini API
- `source`: URL or source of the data
- `sentiment`: Sentiment score (-1.0 to 1.0)
- `created_at`: Timestamp of data entry

### Troubleshooting

**PostgreSQL not found:**
```bash
which psql  # Should return path to psql
```
If not found, install PostgreSQL (see step 1 above)

**PostgreSQL not running:**
```bash
pg_isready  # Check if PostgreSQL is accepting connections
```

**Database connection errors:**
- Check `.env` file has correct credentials
- Verify database exists: `psql -U postgres -l`
- Test connection: `psql -U postgres -d celebrity_index`

### Part 1 Checklist

- [x] Virtual environment created
- [x] Dependencies installed
- [x] Project structure created
- [x] `.env` template created
- [x] API config module created
- [x] Database schema designed
- [x] Database connection module created
- [ ] PostgreSQL installed (REQUIRED)
- [ ] Database created (REQUIRED)
- [ ] Schema applied (REQUIRED)
- [ ] API keys configured (REQUIRED)
- [ ] Database connection tested (REQUIRED)

---

**Status**: Part 1 code is complete. PostgreSQL installation and configuration required.

**Next**: After completing PostgreSQL setup, proceed to Part 2 (Data Collection Module).
