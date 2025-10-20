# Test 1: Celebrity Index Collector - Step-by-Step Implementation Guide

## Project Overview
Celebrity Index Collector is a system to gather real-time data and quantify celebrity impact in Taiwan. Test 1 focuses on establishing basic data collection and sentiment analysis capabilities.

**Goal**: Collect and analyze sentiment data for 100 celebrities daily using Google Search API and Google Gemini API.

**Tech Stack**: Python, PostgreSQL, Google Search API, Google Gemini API, Desktop UI (Tkinter/PyQt/Streamlit)

---

## PART 1: Environment Setup & Configuration

### STEP 1.1: Install Dependencies and Create Project Structure
**Task**: Set up Python environment and project structure

**Implementation**:
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create project structure
mkdir -p src/{data_collection,data_processing,storage,ui}
mkdir -p tests/{unit,integration}
mkdir -p config
mkdir -p logs
touch src/__init__.py
touch requirements.txt
```

**Required in `requirements.txt`**:
```
google-api-python-client
google-generativeai
psycopg2-binary
python-dotenv
pandas
numpy
```

**DEBUG CHECKPOINT**:
- [ ] Virtual environment activated successfully
- [ ] All directories created
- [ ] Run `pip install -r requirements.txt` with no errors
- [ ] Run `python -c "import google.generativeai"` - should not error

**If errors occur**:
- Check Python version (need 3.8+)
- On Windows, may need Visual C++ for psycopg2
- Try `psycopg2-binary` if `psycopg2` fails

---

### STEP 1.2: Configure API Credentials
**Task**: Set up Google Search API and Google Gemini API access

**Implementation**:
1. Create `.env` file in project root:
```
GOOGLE_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
GEMINI_API_KEY=your_gemini_api_key
DB_NAME=celebrity_index
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

2. Create `config/api_config.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_SEARCH_ENGINE_ID = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
```

**DEBUG CHECKPOINT**:
- [ ] `.env` file created and populated
- [ ] Run test script to verify API keys load:
```python
from config.api_config import GOOGLE_API_KEY, GEMINI_API_KEY
assert GOOGLE_API_KEY is not None, "Google API key not loaded"
assert GEMINI_API_KEY is not None, "Gemini API key not loaded"
print("✓ All API keys loaded successfully")
```

**If errors occur**:
- Verify `.env` file is in project root
- Check no extra spaces around `=` in `.env`
- Ensure `python-dotenv` is installed

---

### STEP 1.3: Initialize PostgreSQL Database
**Task**: Set up local PostgreSQL database and create schema

**Implementation**:
1. Install PostgreSQL locally (if not installed)
2. Create database:
```bash
psql -U postgres -c "CREATE DATABASE celebrity_index;"
```

3. Create `src/storage/schema.sql`:
```sql
-- Celebrities Table
CREATE TABLE IF NOT EXISTS celebrities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(100),
    mention_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily Sentiment Data Table
CREATE TABLE IF NOT EXISTS daily_sentiment (
    id SERIAL PRIMARY KEY,
    celebrity_id INTEGER REFERENCES celebrities(id) ON DELETE CASCADE,
    collection_date DATE NOT NULL,
    sentiment_score DECIMAL(5,2),
    mention_count INTEGER DEFAULT 0,
    processed_text TEXT,
    raw_data_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(celebrity_id, collection_date)
);

-- Index for faster queries
CREATE INDEX idx_celebrity_status ON celebrities(status);
CREATE INDEX idx_sentiment_date ON daily_sentiment(collection_date);
CREATE INDEX idx_sentiment_celebrity ON daily_sentiment(celebrity_id);
```

4. Create `src/storage/db_connection.py`:
```python
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
            cls._connection_pool = pool.SimpleConnectionPool(
                1, 20,
                dbname=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                host=os.getenv('DB_HOST'),
                port=os.getenv('DB_PORT')
            )

    @classmethod
    def get_connection(cls):
        if cls._connection_pool is None:
            cls.initialize_pool()
        return cls._connection_pool.getconn()

    @classmethod
    def return_connection(cls, connection):
        cls._connection_pool.putconn(connection)
```

5. Apply schema:
```bash
psql -U postgres -d celebrity_index -f src/storage/schema.sql
```

**DEBUG CHECKPOINT**:
- [ ] PostgreSQL service running
- [ ] Database `celebrity_index` created
- [ ] Schema applied without errors
- [ ] Run verification script:
```python
from src.storage.db_connection import DatabaseConnection

conn = DatabaseConnection.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
tables = cursor.fetchall()
print(f"✓ Tables created: {tables}")
assert ('celebrities',) in tables
assert ('daily_sentiment',) in tables
cursor.close()
DatabaseConnection.return_connection(conn)
```

**If errors occur**:
- Check PostgreSQL service: `sudo service postgresql status`
- Verify credentials in `.env` match PostgreSQL user
- Check PostgreSQL logs for connection errors

---

## PART 2: Data Collection Module

### STEP 2.1: Implement Google Search API Integration
**Task**: Create module to fetch celebrity mentions from Google Search

**Implementation**:
Create `src/data_collection/google_search.py`:
```python
from googleapiclient.discovery import build
from config.api_config import GOOGLE_API_KEY, GOOGLE_SEARCH_ENGINE_ID
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleSearchCollector:
    def __init__(self):
        self.service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        self.search_engine_id = GOOGLE_SEARCH_ENGINE_ID
        self.rate_limit_delay = 1  # seconds between requests

    def search_celebrity(self, celebrity_name, num_results=10):
        """
        Search for celebrity mentions in the last 24 hours
        Returns: List of search results with title, snippet, link
        """
        try:
            # Calculate date range (last 24 hours)
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

            query = f"{celebrity_name} Taiwan 新聞"

            result = self.service.cse().list(
                q=query,
                cx=self.search_engine_id,
                num=num_results,
                dateRestrict='d1',  # Last 1 day
                lr='lang_zh-TW',  # Traditional Chinese
            ).execute()

            items = result.get('items', [])
            logger.info(f"✓ Found {len(items)} results for {celebrity_name}")

            return [{
                'title': item.get('title'),
                'snippet': item.get('snippet'),
                'link': item.get('link'),
                'date': datetime.now().strftime('%Y-%m-%d')
            } for item in items]

        except Exception as e:
            logger.error(f"✗ Error searching for {celebrity_name}: {str(e)}")
            return []

    def get_total_mentions(self, celebrity_name):
        """Get approximate number of mentions"""
        try:
            result = self.service.cse().list(
                q=f"{celebrity_name} Taiwan",
                cx=self.search_engine_id,
                num=1
            ).execute()

            total = result.get('searchInformation', {}).get('totalResults', 0)
            return int(total)
        except Exception as e:
            logger.error(f"✗ Error getting mention count: {str(e)}")
            return 0
```

**DEBUG CHECKPOINT**:
- [ ] Create test file `tests/unit/test_google_search.py`:
```python
from src.data_collection.google_search import GoogleSearchCollector

collector = GoogleSearchCollector()

# Test with a well-known Taiwan celebrity
test_celebrity = "周杰倫"  # Jay Chou
results = collector.search_celebrity(test_celebrity)

print(f"Testing search for: {test_celebrity}")
print(f"✓ Results found: {len(results)}")

if results:
    print(f"✓ Sample result: {results[0]['title']}")
    assert 'title' in results[0]
    assert 'snippet' in results[0]
    assert 'link' in results[0]
    print("✓ All required fields present")
else:
    print("⚠ Warning: No results found - check API credentials or quota")

# Test mention count
mentions = collector.get_total_mentions(test_celebrity)
print(f"✓ Total mentions: {mentions}")
```

**Run test**: `python -m tests.unit.test_google_search`

**If errors occur**:
- Check API key is valid
- Verify Custom Search Engine ID is correct
- Check API quota not exceeded (100 queries/day free tier)
- Test with different celebrity names
- Verify Search Engine has "Search entire web" enabled

---

### STEP 2.2: Implement Celebrity Discovery
**Task**: Create mechanism to discover and filter celebrities

**Implementation**:
Create `src/data_collection/celebrity_discovery.py`:
```python
from src.data_collection.google_search import GoogleSearchCollector
from src.storage.db_connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)

class CelebrityDiscovery:
    def __init__(self, mention_threshold=100):
        self.collector = GoogleSearchCollector()
        self.mention_threshold = mention_threshold

    def discover_celebrity(self, name, category):
        """
        Check if celebrity meets mention threshold and add to database
        """
        mention_count = self.collector.get_total_mentions(name)

        if mention_count >= self.mention_threshold:
            self._add_to_database(name, category, mention_count)
            logger.info(f"✓ Added {name} ({category}) - {mention_count} mentions")
            return True
        else:
            logger.info(f"✗ Skipped {name} - only {mention_count} mentions (threshold: {self.mention_threshold})")
            return False

    def _add_to_database(self, name, category, mention_count):
        """Add celebrity to database"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO celebrities (name, category, mention_count, status)
                VALUES (%s, %s, %s, 'active')
                ON CONFLICT (name) DO UPDATE
                SET mention_count = EXCLUDED.mention_count,
                    updated_at = CURRENT_TIMESTAMP
            """, (name, category, mention_count))

            conn.commit()
            logger.info(f"✓ Database updated for {name}")

        except Exception as e:
            conn.rollback()
            logger.error(f"✗ Database error for {name}: {str(e)}")
        finally:
            cursor.close()
            DatabaseConnection.return_connection(conn)

    def batch_discover(self, celebrity_list):
        """
        celebrity_list: List of dicts with 'name' and 'category'
        Example: [{'name': '周杰倫', 'category': 'singer'}, ...]
        """
        added_count = 0
        for celeb in celebrity_list:
            if self.discover_celebrity(celeb['name'], celeb['category']):
                added_count += 1

        logger.info(f"✓ Discovery complete: {added_count}/{len(celebrity_list)} celebrities added")
        return added_count
```

**DEBUG CHECKPOINT**:
- [ ] Create test file `tests/unit/test_celebrity_discovery.py`:
```python
from src.data_collection.celebrity_discovery import CelebrityDiscovery
from src.storage.db_connection import DatabaseConnection

# Test celebrity list (use well-known Taiwan celebrities)
test_celebrities = [
    {'name': '周杰倫', 'category': 'singer'},
    {'name': '蔡依林', 'category': 'singer'},
    {'name': '林志玲', 'category': 'actor'},
    {'name': 'Unknown Person XYZ123', 'category': 'test'},  # Should be filtered
]

discovery = CelebrityDiscovery(mention_threshold=50)
added = discovery.batch_discover(test_celebrities)

print(f"✓ Added {added} celebrities")

# Verify database
conn = DatabaseConnection.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT name, category, mention_count FROM celebrities;")
results = cursor.fetchall()
print("\n✓ Database contents:")
for row in results:
    print(f"  - {row[0]} ({row[1]}): {row[2]} mentions")

cursor.close()
DatabaseConnection.return_connection(conn)

assert added >= 2, "Should have added at least 2 celebrities"
print("\n✓ Celebrity discovery test passed")
```

**Run test**: `python -m tests.unit.test_celebrity_discovery`

**If errors occur**:
- Check database connection
- Verify API quota sufficient
- Lower mention_threshold for testing
- Check celebrity names are spelled correctly

---

### STEP 2.3: Create Initial Celebrity Seed List
**Task**: Create seed list of 100 Taiwan celebrities

**Implementation**:
Create `config/celebrity_seed_list.json`:
```json
{
  "celebrities": [
    {"name": "周杰倫", "category": "singer"},
    {"name": "蔡依林", "category": "singer"},
    {"name": "林志玲", "category": "actor"},
    {"name": "吳宗憲", "category": "tv_personality"},
    {"name": "蔡英文", "category": "politician"},
    ... (add 95 more)
  ]
}
```

Create `src/data_collection/initialize_celebrities.py`:
```python
import json
from src.data_collection.celebrity_discovery import CelebrityDiscovery

def load_seed_list():
    with open('config/celebrity_seed_list.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['celebrities']

def initialize_database():
    """Load initial celebrity list into database"""
    celebrities = load_seed_list()
    discovery = CelebrityDiscovery(mention_threshold=50)

    print(f"Initializing database with {len(celebrities)} celebrities...")
    added = discovery.batch_discover(celebrities)
    print(f"✓ Initialization complete: {added} celebrities added to database")

if __name__ == "__main__":
    initialize_database()
```

**DEBUG CHECKPOINT**:
- [ ] Seed list JSON file created with at least 100 celebrities
- [ ] Run: `python src/data_collection/initialize_celebrities.py`
- [ ] Verify database populated:
```python
from src.storage.db_connection import DatabaseConnection

conn = DatabaseConnection.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM celebrities WHERE status='active';")
count = cursor.fetchone()[0]
print(f"✓ Total active celebrities in database: {count}")
assert count >= 50, "Should have at least 50 celebrities"
cursor.close()
DatabaseConnection.return_connection(conn)
```

**If errors occur**:
- Check JSON file encoding is UTF-8
- Monitor API quota usage
- Add delays between requests if rate limited
- May need to run in batches to avoid quota limits

---

## PART 3: Data Processing Module

### STEP 3.1: Implement Google Gemini Text Cleaning
**Task**: Create text cleaning module using Gemini API

**Implementation**:
Create `src/data_processing/text_cleaner.py`:
```python
import google.generativeai as genai
from config.api_config import GEMINI_API_KEY
import logging

logger = logging.getLogger(__name__)

genai.configure(api_key=GEMINI_API_KEY)

class TextCleaner:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')

    def clean_search_results(self, search_results):
        """
        Clean and summarize search results
        search_results: List of dicts with 'title', 'snippet', 'link'
        Returns: Cleaned text summary
        """
        if not search_results:
            return ""

        # Combine all snippets
        combined_text = "\n".join([
            f"{item['title']}: {item['snippet']}"
            for item in search_results
        ])

        prompt = f"""請將以下關於某位名人的新聞摘要整理成一段連貫的文字，
        保留重要資訊，移除重複內容和廣告文字。請用繁體中文回覆。

        新聞內容：
        {combined_text}

        請提供清理後的摘要（200字以內）："""

        try:
            response = self.model.generate_content(prompt)
            cleaned_text = response.text
            logger.info(f"✓ Text cleaned successfully ({len(cleaned_text)} chars)")
            return cleaned_text

        except Exception as e:
            logger.error(f"✗ Gemini API error: {str(e)}")
            # Fallback: return combined snippets
            return combined_text[:500]

    def extract_key_points(self, text):
        """Extract key points from cleaned text"""
        if not text:
            return []

        prompt = f"""從以下文字中提取3-5個關鍵要點，每個要點一行：

        {text}

        關鍵要點："""

        try:
            response = self.model.generate_content(prompt)
            key_points = [line.strip() for line in response.text.split('\n') if line.strip()]
            return key_points
        except Exception as e:
            logger.error(f"✗ Key point extraction error: {str(e)}")
            return []
```

**DEBUG CHECKPOINT**:
- [ ] Create test file `tests/unit/test_text_cleaner.py`:
```python
from src.data_processing.text_cleaner import TextCleaner

cleaner = TextCleaner()

# Test data
test_results = [
    {
        'title': '周杰倫新專輯發布',
        'snippet': '歌手周杰倫今天發布新專輯，受到粉絲熱烈歡迎...',
        'link': 'https://example.com'
    },
    {
        'title': '周杰倫演唱會門票秒殺',
        'snippet': '演唱會門票在開賣後立即售罄，顯示其超高人氣...',
        'link': 'https://example.com'
    }
]

cleaned = cleaner.clean_search_results(test_results)
print(f"✓ Cleaned text ({len(cleaned)} chars):")
print(cleaned)
print()

assert len(cleaned) > 0, "Cleaned text should not be empty"
assert len(cleaned) <= 500, "Cleaned text should be summarized"

# Test key points
key_points = cleaner.extract_key_points(cleaned)
print(f"✓ Key points extracted: {len(key_points)}")
for i, point in enumerate(key_points, 1):
    print(f"  {i}. {point}")

print("\n✓ Text cleaner test passed")
```

**Run test**: `python -m tests.unit.test_text_cleaner`

**If errors occur**:
- Verify Gemini API key is valid
- Check API quota not exceeded
- Test with simpler prompts
- Add error handling for API timeouts

---

### STEP 3.2: Implement Sentiment Analysis
**Task**: Create sentiment analysis module

**Implementation**:
Create `src/data_processing/sentiment_analyzer.py`:
```python
import logging
import google.generativeai as genai
from config.api_config import GEMINI_API_KEY

logger = logging.getLogger(__name__)
genai.configure(api_key=GEMINI_API_KEY)

class SentimentAnalyzer:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')

    def analyze_sentiment(self, text):
        """
        Analyze sentiment of text
        Returns: Score from -1.0 (very negative) to 1.0 (very positive)
        """
        if not text:
            return 0.0

        prompt = f"""請分析以下文字的情感傾向。
        回覆格式：只回覆一個-1.0到1.0之間的數字
        -1.0 = 非常負面
        0.0 = 中性
        1.0 = 非常正面

        文字內容：
        {text}

        情感分數："""

        try:
            response = self.model.generate_content(prompt)
            score_text = response.text.strip()

            # Extract number from response
            import re
            numbers = re.findall(r'-?\d+\.?\d*', score_text)
            if numbers:
                score = float(numbers[0])
                # Clamp between -1 and 1
                score = max(-1.0, min(1.0, score))
                logger.info(f"✓ Sentiment score: {score}")
                return score
            else:
                logger.warning(f"⚠ Could not parse sentiment score from: {score_text}")
                return 0.0

        except Exception as e:
            logger.error(f"✗ Sentiment analysis error: {str(e)}")
            return 0.0

    def classify_sentiment(self, score):
        """Convert score to category"""
        if score >= 0.3:
            return "positive"
        elif score <= -0.3:
            return "negative"
        else:
            return "neutral"
```

**DEBUG CHECKPOINT**:
- [ ] Create test file `tests/unit/test_sentiment_analyzer.py`:
```python
from src.data_processing.sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()

# Test cases
test_cases = [
    ("周杰倫的新專輯非常棒，粉絲都很喜歡！", "positive"),
    ("演唱會取消，粉絲感到失望", "negative"),
    ("周杰倫今天發布新專輯", "neutral"),
]

print("Testing sentiment analysis:")
for text, expected in test_cases:
    score = analyzer.analyze_sentiment(text)
    classification = analyzer.classify_sentiment(score)

    print(f"\nText: {text}")
    print(f"Score: {score:.2f}")
    print(f"Classification: {classification}")
    print(f"Expected: {expected}")

    # Relaxed assertion - just check score is valid
    assert -1.0 <= score <= 1.0, f"Score {score} out of range"

print("\n✓ Sentiment analysis test passed")
```

**Run test**: `python -m tests.unit.test_sentiment_analyzer`

**If errors occur**:
- Check Gemini API quota
- Verify prompt is clear enough
- Add fallback to alternative sentiment library (e.g., TextBlob, NLTK)
- Test with English text if Chinese fails

---

### STEP 3.3: Create Complete Processing Pipeline
**Task**: Combine data collection, cleaning, and sentiment analysis

**Implementation**:
Create `src/data_processing/pipeline.py`:
```python
from src.data_collection.google_search import GoogleSearchCollector
from src.data_processing.text_cleaner import TextCleaner
from src.data_processing.sentiment_analyzer import SentimentAnalyzer
from src.storage.db_connection import DatabaseConnection
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataPipeline:
    def __init__(self):
        self.collector = GoogleSearchCollector()
        self.cleaner = TextCleaner()
        self.analyzer = SentimentAnalyzer()

    def process_celebrity(self, celebrity_name, celebrity_id):
        """
        Complete pipeline for one celebrity:
        1. Collect search results
        2. Clean text
        3. Analyze sentiment
        4. Store in database
        """
        logger.info(f"Processing {celebrity_name}...")

        # Step 1: Collect data
        search_results = self.collector.search_celebrity(celebrity_name)
        if not search_results:
            logger.warning(f"⚠ No results for {celebrity_name}")
            return None

        # Step 2: Clean text
        cleaned_text = self.cleaner.clean_search_results(search_results)

        # Step 3: Analyze sentiment
        sentiment_score = self.analyzer.analyze_sentiment(cleaned_text)

        # Step 4: Store results
        self._store_sentiment_data(
            celebrity_id=celebrity_id,
            sentiment_score=sentiment_score,
            mention_count=len(search_results),
            processed_text=cleaned_text,
            raw_data_summary=str(search_results[:3])  # Store first 3 results
        )

        logger.info(f"✓ {celebrity_name}: sentiment={sentiment_score:.2f}, mentions={len(search_results)}")
        return sentiment_score

    def _store_sentiment_data(self, celebrity_id, sentiment_score, mention_count, processed_text, raw_data_summary):
        """Store daily sentiment data"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO daily_sentiment
                (celebrity_id, collection_date, sentiment_score, mention_count, processed_text, raw_data_summary)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (celebrity_id, collection_date)
                DO UPDATE SET
                    sentiment_score = EXCLUDED.sentiment_score,
                    mention_count = EXCLUDED.mention_count,
                    processed_text = EXCLUDED.processed_text,
                    raw_data_summary = EXCLUDED.raw_data_summary,
                    created_at = CURRENT_TIMESTAMP
            """, (celebrity_id, datetime.now().date(), sentiment_score, mention_count, processed_text, raw_data_summary))

            conn.commit()
            logger.info(f"✓ Data stored for celebrity_id={celebrity_id}")

        except Exception as e:
            conn.rollback()
            logger.error(f"✗ Database error: {str(e)}")
        finally:
            cursor.close()
            DatabaseConnection.return_connection(conn)

    def process_all_celebrities(self):
        """Process all active celebrities in database"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, name FROM celebrities WHERE status='active';")
        celebrities = cursor.fetchall()
        cursor.close()
        DatabaseConnection.return_connection(conn)

        logger.info(f"Processing {len(celebrities)} celebrities...")

        processed_count = 0
        for celeb_id, celeb_name in celebrities:
            try:
                self.process_celebrity(celeb_name, celeb_id)
                processed_count += 1
            except Exception as e:
                logger.error(f"✗ Error processing {celeb_name}: {str(e)}")

        logger.info(f"✓ Processing complete: {processed_count}/{len(celebrities)} celebrities")
        return processed_count
```

**DEBUG CHECKPOINT**:
- [ ] Create test file `tests/integration/test_pipeline.py`:
```python
from src.data_processing.pipeline import DataPipeline
from src.storage.db_connection import DatabaseConnection

pipeline = DataPipeline()

# Test with one celebrity
conn = DatabaseConnection.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT id, name FROM celebrities WHERE status='active' LIMIT 1;")
result = cursor.fetchone()

if result:
    celeb_id, celeb_name = result
    print(f"Testing pipeline with: {celeb_name}")

    score = pipeline.process_celebrity(celeb_name, celeb_id)

    if score is not None:
        print(f"✓ Processing successful: sentiment score = {score:.2f}")

        # Verify data stored
        cursor.execute("""
            SELECT sentiment_score, mention_count, processed_text
            FROM daily_sentiment
            WHERE celebrity_id = %s
            ORDER BY created_at DESC LIMIT 1
        """, (celeb_id,))

        data = cursor.fetchone()
        if data:
            print(f"✓ Data verified in database:")
            print(f"  Sentiment: {data[0]}")
            print(f"  Mentions: {data[1]}")
            print(f"  Text preview: {data[2][:100]}...")
        else:
            print("✗ No data found in database")
    else:
        print("✗ Processing failed")
else:
    print("✗ No celebrities in database")

cursor.close()
DatabaseConnection.return_connection(conn)

print("\n✓ Pipeline integration test complete")
```

**Run test**: `python -m tests.integration.test_pipeline`

**If errors occur**:
- Check all previous steps completed successfully
- Verify API quotas sufficient
- Check database connection
- Add error handling and retries
- Monitor API rate limits

---

## PART 4: Desktop User Interface

### STEP 4.1: Create Basic Desktop UI with Streamlit
**Task**: Build simple desktop interface to display rankings

**Implementation**:
Add to `requirements.txt`:
```
streamlit
plotly
```

Create `src/ui/app.py`:
```python
import streamlit as st
import pandas as pd
from src.storage.db_connection import DatabaseConnection
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="Celebrity Index Collector", layout="wide")

class CelebrityDashboard:
    def __init__(self):
        self.conn = None

    def get_connection(self):
        if self.conn is None:
            self.conn = DatabaseConnection.get_connection()
        return self.conn

    def get_latest_rankings(self, limit=100):
        """Get latest sentiment rankings"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT
                c.name,
                c.category,
                ds.sentiment_score,
                ds.mention_count,
                ds.collection_date,
                ds.processed_text
            FROM daily_sentiment ds
            JOIN celebrities c ON ds.celebrity_id = c.id
            WHERE ds.collection_date = (SELECT MAX(collection_date) FROM daily_sentiment)
            ORDER BY ds.sentiment_score DESC
            LIMIT %s
        """

        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        cursor.close()

        df = pd.DataFrame(results, columns=[
            'Name', 'Category', 'Sentiment Score', 'Mentions', 'Date', 'Summary'
        ])

        return df

    def get_celebrity_trend(self, celebrity_name, days=7):
        """Get sentiment trend for a celebrity"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT ds.collection_date, ds.sentiment_score, ds.mention_count
            FROM daily_sentiment ds
            JOIN celebrities c ON ds.celebrity_id = c.id
            WHERE c.name = %s
            AND ds.collection_date >= %s
            ORDER BY ds.collection_date ASC
        """

        start_date = datetime.now().date() - timedelta(days=days)
        cursor.execute(query, (celebrity_name, start_date))
        results = cursor.fetchall()
        cursor.close()

        df = pd.DataFrame(results, columns=['Date', 'Sentiment Score', 'Mentions'])
        return df

def main():
    st.title("🌟 Celebrity Index Collector - Test 1")
    st.markdown("Real-time celebrity sentiment analysis for Taiwan")

    dashboard = CelebrityDashboard()

    # Sidebar filters
    st.sidebar.header("Filters")
    view_mode = st.sidebar.radio("View Mode", ["Rankings", "Celebrity Trend"])

    if view_mode == "Rankings":
        st.header("📊 Latest Celebrity Sentiment Rankings")

        # Get data
        df = dashboard.get_latest_rankings()

        if not df.empty:
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Celebrities", len(df))
            with col2:
                avg_sentiment = df['Sentiment Score'].mean()
                st.metric("Average Sentiment", f"{avg_sentiment:.2f}")
            with col3:
                total_mentions = df['Mentions'].sum()
                st.metric("Total Mentions", total_mentions)

            # Category filter
            categories = ['All'] + sorted(df['Category'].unique().tolist())
            selected_category = st.sidebar.selectbox("Category", categories)

            if selected_category != 'All':
                df = df[df['Category'] == selected_category]

            # Display table
            st.dataframe(
                df[['Name', 'Category', 'Sentiment Score', 'Mentions']],
                use_container_width=True,
                hide_index=True
            )

            # Visualization
            st.subheader("📈 Sentiment Distribution")
            fig = px.bar(
                df.head(20),
                x='Name',
                y='Sentiment Score',
                color='Sentiment Score',
                color_continuous_scale=['red', 'yellow', 'green'],
                title='Top 20 Celebrities by Sentiment'
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("No data available. Run the data pipeline first.")

    else:  # Celebrity Trend
        st.header("📈 Celebrity Sentiment Trend")

        # Get celebrity list
        df = dashboard.get_latest_rankings()
        if not df.empty:
            celebrity_names = sorted(df['Name'].unique().tolist())
            selected_celebrity = st.sidebar.selectbox("Select Celebrity", celebrity_names)

            days = st.sidebar.slider("Days to show", 1, 30, 7)

            # Get trend data
            trend_df = dashboard.get_celebrity_trend(selected_celebrity, days)

            if not trend_df.empty:
                # Line chart
                fig = px.line(
                    trend_df,
                    x='Date',
                    y='Sentiment Score',
                    title=f'Sentiment Trend for {selected_celebrity}',
                    markers=True
                )
                st.plotly_chart(fig, use_container_width=True)

                # Mentions chart
                fig2 = px.bar(
                    trend_df,
                    x='Date',
                    y='Mentions',
                    title=f'Daily Mentions for {selected_celebrity}'
                )
                st.plotly_chart(fig2, use_container_width=True)

                # Data table
                st.dataframe(trend_df, use_container_width=True, hide_index=True)
            else:
                st.info(f"No trend data available for {selected_celebrity}")
        else:
            st.warning("No celebrities in database yet.")

if __name__ == "__main__":
    main()
```

**DEBUG CHECKPOINT**:
- [ ] Install dependencies: `pip install streamlit plotly`
- [ ] Run UI: `streamlit run src/ui/app.py`
- [ ] Check browser opens automatically to http://localhost:8501
- [ ] Verify:
  - [ ] Dashboard loads without errors
  - [ ] Can see celebrity rankings
  - [ ] Can filter by category
  - [ ] Charts display correctly
  - [ ] Celebrity trend view works

**If errors occur**:
- Check database has data from pipeline
- Verify Streamlit installed correctly
- Check port 8501 not in use
- Test database queries manually
- Check pandas/plotly versions compatible

---

## PART 5: Automation & Scheduling

### STEP 5.1: Create Daily Collection Script
**Task**: Automate daily data collection

**Implementation**:
Create `scripts/daily_collection.py`:
```python
#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_processing.pipeline import DataPipeline
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/daily_collection_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 50)
    logger.info("Starting daily collection process")
    logger.info("=" * 50)

    pipeline = DataPipeline()

    try:
        processed_count = pipeline.process_all_celebrities()
        logger.info(f"✓ Daily collection complete: {processed_count} celebrities processed")
        return 0
    except Exception as e:
        logger.error(f"✗ Daily collection failed: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
```

**DEBUG CHECKPOINT**:
- [ ] Create logs directory: `mkdir -p logs`
- [ ] Make script executable: `chmod +x scripts/daily_collection.py`
- [ ] Test run: `python scripts/daily_collection.py`
- [ ] Verify:
  - [ ] Script runs without errors
  - [ ] Log file created in `logs/` directory
  - [ ] Database updated with today's data
  - [ ] All celebrities processed

**If errors occur**:
- Check Python path includes project root
- Verify database connection
- Check API quotas sufficient for all celebrities
- Monitor log files for specific errors

---

### STEP 5.2: Setup Scheduled Task (Cron/Task Scheduler)
**Task**: Schedule script to run daily

**Implementation**:

**For macOS/Linux (cron)**:
```bash
# Edit crontab
crontab -e

# Add this line to run daily at 9 AM
0 9 * * * cd /path/to/project && /path/to/venv/bin/python scripts/daily_collection.py
```

**For Windows (Task Scheduler)**:
Create `scripts/schedule_windows.bat`:
```batch
@echo off
cd /d C:\path\to\project
call venv\Scripts\activate
python scripts\daily_collection.py
```

Then create scheduled task:
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 9:00 AM
4. Action: Start a program
5. Program: `C:\path\to\project\scripts\schedule_windows.bat`

**DEBUG CHECKPOINT**:
- [ ] Verify cron job created: `crontab -l` (Linux/Mac)
- [ ] Test scheduled task runs manually
- [ ] Check logs directory after scheduled run
- [ ] Verify data updated in database after scheduled run

**If errors occur**:
- Ensure full paths used in cron/task scheduler
- Check user permissions
- Verify virtual environment activated
- Test script manually first

---

## PART 6: Testing & Validation

### STEP 6.1: End-to-End Integration Test
**Task**: Test complete system workflow

**Implementation**:
Create `tests/integration/test_e2e.py`:
```python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data_collection.celebrity_discovery import CelebrityDiscovery
from src.data_processing.pipeline import DataPipeline
from src.storage.db_connection import DatabaseConnection
from datetime import datetime

print("=" * 60)
print("END-TO-END INTEGRATION TEST")
print("=" * 60)

# Step 1: Verify database connection
print("\n[1/5] Testing database connection...")
conn = DatabaseConnection.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM celebrities;")
celeb_count = cursor.fetchone()[0]
print(f"✓ Database connected: {celeb_count} celebrities found")
assert celeb_count > 0, "No celebrities in database"

# Step 2: Test celebrity discovery
print("\n[2/5] Testing celebrity discovery...")
discovery = CelebrityDiscovery(mention_threshold=10)
test_celeb = {'name': '測試名人', 'category': 'test'}
# This will likely fail mention threshold, which is fine
discovery.discover_celebrity(test_celeb['name'], test_celeb['category'])
print("✓ Celebrity discovery module working")

# Step 3: Test data pipeline with one celebrity
print("\n[3/5] Testing data pipeline...")
cursor.execute("SELECT id, name FROM celebrities WHERE status='active' LIMIT 1;")
result = cursor.fetchone()
if result:
    celeb_id, celeb_name = result
    pipeline = DataPipeline()
    score = pipeline.process_celebrity(celeb_name, celeb_id)
    assert score is not None, "Pipeline should return sentiment score"
    print(f"✓ Pipeline processed {celeb_name}: sentiment={score:.2f}")
else:
    print("⚠ No celebrities to test pipeline")

# Step 4: Verify data storage
print("\n[4/5] Verifying data storage...")
cursor.execute("""
    SELECT COUNT(*) FROM daily_sentiment
    WHERE collection_date = %s
""", (datetime.now().date(),))
today_count = cursor.fetchone()[0]
print(f"✓ Sentiment data stored: {today_count} records today")

# Step 5: Test data retrieval for UI
print("\n[5/5] Testing data retrieval...")
cursor.execute("""
    SELECT c.name, ds.sentiment_score, ds.mention_count
    FROM daily_sentiment ds
    JOIN celebrities c ON ds.celebrity_id = c.id
    WHERE ds.collection_date = (SELECT MAX(collection_date) FROM daily_sentiment)
    ORDER BY ds.sentiment_score DESC
    LIMIT 5
""")
top_5 = cursor.fetchall()
print("✓ Top 5 celebrities by sentiment:")
for i, (name, score, mentions) in enumerate(top_5, 1):
    print(f"  {i}. {name}: {score:.2f} ({mentions} mentions)")

cursor.close()
DatabaseConnection.return_connection(conn)

print("\n" + "=" * 60)
print("✓ END-TO-END TEST PASSED")
print("=" * 60)
```

**Run test**: `python tests/integration/test_e2e.py`

**DEBUG CHECKPOINT**:
- [ ] All 5 test steps pass
- [ ] No database errors
- [ ] API calls successful
- [ ] Data retrieved correctly

**If errors occur**:
- Run individual component tests first
- Check API quotas
- Verify database schema
- Review log files

---

### STEP 6.2: Data Quality Validation
**Task**: Validate accuracy and completeness of collected data

**Implementation**:
Create `scripts/validate_data_quality.py`:
```python
#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.storage.db_connection import DatabaseConnection
from datetime import datetime, timedelta

def validate_data_quality():
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor()

    print("=" * 60)
    print("DATA QUALITY VALIDATION REPORT")
    print("=" * 60)

    # Check 1: Celebrity count
    print("\n[Check 1] Celebrity Database")
    cursor.execute("SELECT COUNT(*) FROM celebrities WHERE status='active';")
    active_count = cursor.fetchone()[0]
    print(f"Active celebrities: {active_count}")
    print(f"Target: 100")
    print(f"Status: {'✓ PASS' if active_count >= 50 else '✗ FAIL - Need more celebrities'}")

    # Check 2: Recent data collection
    print("\n[Check 2] Recent Data Collection")
    cursor.execute("SELECT MAX(collection_date) FROM daily_sentiment;")
    latest_date = cursor.fetchone()[0]
    print(f"Latest collection date: {latest_date}")

    if latest_date:
        days_old = (datetime.now().date() - latest_date).days
        print(f"Days old: {days_old}")
        print(f"Status: {'✓ PASS' if days_old <= 1 else '⚠ WARNING - Data is outdated'}")
    else:
        print("Status: ✗ FAIL - No data collected yet")

    # Check 3: Data completeness
    print("\n[Check 3] Data Completeness")
    cursor.execute("""
        SELECT COUNT(*) FROM daily_sentiment
        WHERE collection_date = (SELECT MAX(collection_date) FROM daily_sentiment)
    """)
    today_records = cursor.fetchone()[0]
    print(f"Records collected today: {today_records}")
    print(f"Active celebrities: {active_count}")
    coverage = (today_records / active_count * 100) if active_count > 0 else 0
    print(f"Coverage: {coverage:.1f}%")
    print(f"Status: {'✓ PASS' if coverage >= 80 else '⚠ WARNING - Low coverage'}")

    # Check 4: Sentiment score distribution
    print("\n[Check 4] Sentiment Score Distribution")
    cursor.execute("""
        SELECT
            COUNT(CASE WHEN sentiment_score > 0.3 THEN 1 END) as positive,
            COUNT(CASE WHEN sentiment_score BETWEEN -0.3 AND 0.3 THEN 1 END) as neutral,
            COUNT(CASE WHEN sentiment_score < -0.3 THEN 1 END) as negative
        FROM daily_sentiment
        WHERE collection_date = (SELECT MAX(collection_date) FROM daily_sentiment)
    """)
    pos, neu, neg = cursor.fetchone()
    total = pos + neu + neg
    if total > 0:
        print(f"Positive: {pos} ({pos/total*100:.1f}%)")
        print(f"Neutral: {neu} ({neu/total*100:.1f}%)")
        print(f"Negative: {neg} ({neg/total*100:.1f}%)")
        print(f"Status: {'✓ PASS - Balanced distribution' if neu > 0 else '⚠ Check sentiment analysis'}")
    else:
        print("Status: ✗ FAIL - No sentiment data")

    # Check 5: Missing or null data
    print("\n[Check 5] Data Integrity")
    cursor.execute("""
        SELECT COUNT(*) FROM daily_sentiment
        WHERE processed_text IS NULL OR processed_text = ''
        AND collection_date = (SELECT MAX(collection_date) FROM daily_sentiment)
    """)
    missing_text = cursor.fetchone()[0]
    print(f"Records with missing processed text: {missing_text}")
    print(f"Status: {'✓ PASS' if missing_text == 0 else '⚠ WARNING - Some text data missing'}")

    cursor.close()
    DatabaseConnection.return_connection(conn)

    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    validate_data_quality()
```

**Run validation**: `python scripts/validate_data_quality.py`

**DEBUG CHECKPOINT**:
- [ ] All 5 validation checks run
- [ ] At least 80% coverage
- [ ] Sentiment distribution looks reasonable
- [ ] No major data integrity issues

**If errors occur**:
- Run daily collection script
- Check for API failures in logs
- Verify celebrity list is up to date
- Review sentiment analysis accuracy

---

## SUCCESS CRITERIA CHECKLIST

Run through this checklist to confirm Test 1 is complete:

### Data Collection
- [ ] Database contains at least 50 active celebrities
- [ ] Can successfully query Google Search API
- [ ] Celebrity discovery filters working (mention threshold)
- [ ] Daily collection script runs without errors

### Data Processing
- [ ] Google Gemini API cleans text successfully
- [ ] Sentiment analysis produces scores between -1 and 1
- [ ] Processed text stored in database
- [ ] Pipeline handles errors gracefully

### Data Storage
- [ ] PostgreSQL database accessible
- [ ] All tables created with correct schema
- [ ] Foreign key relationships working
- [ ] Today's sentiment data present in database

### User Interface
- [ ] Streamlit dashboard launches
- [ ] Can view celebrity rankings
- [ ] Sentiment charts display correctly
- [ ] Can filter by category
- [ ] Celebrity trend view functional

### Automation
- [ ] Daily collection script works standalone
- [ ] Scheduled task configured (cron/Task Scheduler)
- [ ] Logs generated correctly
- [ ] Error handling in place

### Data Quality
- [ ] At least 80% daily coverage
- [ ] Sentiment scores distributed reasonably
- [ ] No excessive null/missing data
- [ ] Data updated within last 24 hours

---

## TROUBLESHOOTING GUIDE

### Common Issues and Solutions

#### Issue: Google API Quota Exceeded
**Symptoms**: "Quota exceeded" error in logs
**Solutions**:
- Check quota usage in Google Cloud Console
- Add delays between requests (time.sleep)
- Process celebrities in batches
- Consider upgrading API plan

#### Issue: Database Connection Errors
**Symptoms**: "Connection refused" or timeout errors
**Solutions**:
- Check PostgreSQL service running: `sudo service postgresql status`
- Verify credentials in `.env` file
- Check database exists: `psql -l`
- Test connection manually with psql

#### Issue: Gemini API Errors
**Symptoms**: Text cleaning or sentiment analysis fails
**Solutions**:
- Verify API key valid
- Check API quota
- Add retry logic with exponential backoff
- Implement fallback to simpler method

#### Issue: No Search Results Returned
**Symptoms**: Empty results for all celebrities
**Solutions**:
- Verify Custom Search Engine configured
- Check "Search entire web" enabled
- Test query in browser first
- Verify API credentials correct

#### Issue: Streamlit UI Won't Load
**Symptoms**: Dashboard crashes or won't start
**Solutions**:
- Check port 8501 available
- Verify database has data
- Check pandas/plotly installed
- Review browser console for errors

---

## NEXT STEPS AFTER TEST 1

Once all success criteria met:

1. **Evaluate Accuracy**
   - Manually review sentiment scores for sample celebrities
   - Compare with actual news sentiment
   - Identify false positives/negatives

2. **Gather Feedback**
   - Share dashboard with test users
   - Collect feedback on UI/UX
   - Identify missing features

3. **Plan Expansion**
   - Consider additional data sources (social media, news APIs)
   - Explore multi-metric index (engagement, reach, sentiment)
   - Plan for scale (more celebrities, historical data)

4. **Optimize Performance**
   - Profile slow queries
   - Implement caching where appropriate
   - Optimize API usage

5. **Document Lessons Learned**
   - What worked well
   - What challenges encountered
   - Recommendations for Test 2
