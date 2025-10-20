# Celebrity Index Collector v1.0

A real-time celebrity sentiment analysis system for quantifying celebrity impact in Taiwan. The system collects data from Google Search, processes it using AI text cleaning and sentiment analysis, stores it in PostgreSQL, and visualizes results through an interactive Streamlit dashboard.

## Features

- **Real-time Data Collection**: Google Search API integration for last 24 hours of celebrity mentions
- **AI-Powered Processing**: Google Gemini API for text cleaning and sentiment analysis
- **Sentiment Scoring**: -1.0 (negative) to +1.0 (positive) sentiment scale
- **Interactive Dashboard**: Streamlit UI with rankings, trends, and statistics
- **Celebrity Management**: 100 Taiwan celebrities with automated discovery
- **Historical Tracking**: Track sentiment changes over time
- **Robust Architecture**: Error handling, logging, and connection pooling

## Tech Stack

**Backend**
- Python 3.13
- PostgreSQL 14.19
- Google Search API
- Google Gemini 2.5 Flash API

**Frontend**
- Streamlit 1.50.0
- Plotly 6.3.1

**Data Processing**
- pandas, numpy
- psycopg2 (PostgreSQL driver)

## Project Structure

```
vivi/
├── src/
│   ├── data_collection/      # Google Search API integration
│   │   ├── google_search.py
│   │   └── celebrity_manager.py
│   ├── data_processing/      # Text cleaning & sentiment analysis
│   │   ├── text_cleaner.py
│   │   ├── sentiment_analyzer.py
│   │   └── pipeline.py
│   ├── storage/              # Database layer
│   │   ├── db_connection.py
│   │   └── schema.sql
│   └── ui/                   # Streamlit dashboard
│       └── app.py
├── config/
│   ├── api_config.py         # API configuration
│   └── celebrity_seed_list.json  # 100 celebrities
├── scripts/
│   ├── setup_database.sh     # Database initialization
│   ├── collect_sample_data.py # Sample data collector
│   └── run_ui.sh            # UI launcher
├── tests/
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── requirements.txt
├── .env.example             # Environment template
├── CLAUDE.md               # Claude Code instructions
└── README.md               # This file
```

## Installation

### Prerequisites

- Python 3.13+
- PostgreSQL 14+
- Google Search API key
- Google Gemini API key

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/chatgpt003003-sudo/Vivi_v1.git
cd Vivi_v1
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and database credentials
```

5. **Initialize database**
```bash
# Start PostgreSQL (example for Homebrew on macOS)
brew services start postgresql@14

# Create database and schema
psql -U your_username -c "CREATE DATABASE celebrity_index;"
psql -U your_username -d celebrity_index -f src/storage/schema.sql
```

## Usage

### Launch Dashboard

```bash
./scripts/run_ui.sh
# Or directly:
venv/bin/streamlit run src/ui/app.py
```

Access the dashboard at: **http://localhost:8502**

### Collect Celebrity Data

**Option 1: Sample data (10 celebrities)**
```bash
venv/bin/python scripts/collect_sample_data.py
```

**Option 2: Process specific celebrity**
```python
from src.data_processing.pipeline import DataPipeline

pipeline = DataPipeline()
result = pipeline.process_celebrity('周杰倫')
print(f'{result["name"]}: {result["sentiment"]:.2f}')
```

**Option 3: Batch process from seed list**
```python
from src.data_processing.pipeline import DataPipeline
from src.data_collection.celebrity_manager import CelebrityManager

pipeline = DataPipeline()
celebs = CelebrityManager.load_from_json('config/celebrity_seed_list.json')
summary = pipeline.process_multiple_celebrities(celebs, limit=20)
```

## Dashboard Features

### Rankings View
- Celebrity sentiment rankings
- Sortable data tables (highest/lowest/most recent)
- Top 20 bar chart visualization
- Celebrity detail views with summaries

### Trend View
- Historical sentiment tracking
- Interactive line charts
- Date range selection (1-30 days)
- Positive/negative threshold indicators

### Statistics View
- Total records and unique celebrities
- Average sentiment score
- Sentiment distribution pie chart
- Recent activity feed

## Configuration

### Environment Variables (.env)

```bash
# Google APIs
GOOGLE_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
GEMINI_API_KEY=your_gemini_api_key

# Database
DB_NAME=celebrity_index
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Celebrity Seed List

Edit `config/celebrity_seed_list.json` to add/remove celebrities:
```json
[
  {"name": "周杰倫", "category": "music"},
  {"name": "蔡依林", "category": "music"}
]
```

## Database Schema

```sql
CREATE TABLE celebrity_data (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    cleaned_paragraph TEXT,
    source TEXT,
    sentiment DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Testing

Run unit tests:
```bash
pytest tests/unit/
```

Run integration tests:
```bash
pytest tests/integration/
```

## Development

### Code Structure

- **Data Collection**: `src/data_collection/google_search.py`
  - Collects search results from last 24 hours
  - Rate limiting: 1 second between requests
  - Language filter: Traditional Chinese (zh-TW)

- **Text Cleaning**: `src/data_processing/text_cleaner.py`
  - Uses Google Gemini 2.5 Flash
  - Summarizes and cleans search results
  - Removes ads and duplicate content

- **Sentiment Analysis**: `src/data_processing/sentiment_analyzer.py`
  - Gemini-powered sentiment scoring
  - Range: -1.0 (very negative) to +1.0 (very positive)
  - Thresholds: >0.3 positive, <-0.3 negative

- **Pipeline**: `src/data_processing/pipeline.py`
  - End-to-end processing workflow
  - Handles errors and logging
  - Batch processing support

### Adding New Features

1. Create feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make changes and test

3. Commit and push:
```bash
git add .
git commit -m "Add feature: description"
git push origin feature/your-feature-name
```

4. Create pull request on GitHub

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
ps aux | grep postgres

# Test connection
psql -U your_username -d celebrity_index -c "\dt"
```

### API Rate Limits
- Google Search API: 100 queries/day (free tier)
- Gemini API: 15 requests/minute
- Add delays between requests if hitting limits

### Import Errors
Ensure you're in the project root and virtual environment is activated:
```bash
cd /path/to/Vivi_v1
source venv/bin/activate
```

## Performance

- **Single celebrity processing**: ~5-10 seconds
- **Batch (10 celebrities)**: ~1-2 minutes
- **Database queries**: <500ms with indexing
- **Dashboard load time**: 1-2 seconds

## API Usage

- Google Search API calls: ~2 per celebrity
- Gemini API calls: ~2 per celebrity (cleaning + sentiment)
- Total per celebrity: ~4 API calls

## Compliance & Ethics

- Respects API rate limits
- Collects only public information
- No personal data collection
- Source attribution maintained
- Blacklist support for restricted sources

## Roadmap

### Test 2 (Planned)
- Scale to daily automation for 100 celebrities
- Additional data sources (social media)
- Multi-metric celebrity index
- Enhanced analytics and correlations
- Export functionality (CSV, PDF)

### Future Enhancements
- Real-time alerts for sentiment changes
- Category-based analysis
- Comparison tools
- Mobile-responsive UI
- API endpoints for external access

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## License

Copyright (c) 2025. All rights reserved.

## Acknowledgments

- Google Search API for data collection
- Google Gemini API for AI processing
- Streamlit for dashboard framework
- PostgreSQL for reliable data storage

## Contact

Repository: https://github.com/chatgpt003003-sudo/Vivi_v1

---

**Project Status**: ✓ Test 1 Complete - Production Ready

Built with Claude Code - https://claude.com/claude-code
