# 🚀 Launch the Celebrity Index Collector UI

**Status**: ✅ Ready to Launch
**Debug Tests**: 10/10 Passed
**Data**: 10 celebrities processed

---

## Quick Start (3 Steps)

### 1. Ensure PostgreSQL is Running
```bash
/opt/homebrew/opt/postgresql@14/bin/pg_isready
```
**Expected**: `/tmp:5432 - accepting connections`

### 2. Launch the Dashboard
```bash
./scripts/run_ui.sh
```
**Or**:
```bash
venv/bin/streamlit run src/ui/app.py
```

### 3. Access the UI
Your browser should automatically open to:
```
http://localhost:8501
```

If not, manually navigate to that URL.

---

## What You'll See

### 📊 Rankings View (Default)
The dashboard will open showing:
- **Top Metrics**: Total celebrities, average sentiment, positive count
- **Celebrity Table**: Sortable list with sentiment scores
- **Bar Chart**: Top 20 celebrities by sentiment (color-coded)
- **Details Section**: Click any celebrity to see their full summary

**Sample Data**:
```
蔡依林: 0.80 (Positive)
賴清德: 0.80 (Positive)
侯友宜: 0.70 (Positive)
蔡英文: 0.60 (Positive)
林志玲: 0.00 (Neutral)
林書豪: 0.00 (Neutral)
吳宗憲: -0.60 (Negative)
韓國瑜: -0.80 (Negative)
周杰倫: -0.90 (Negative)
柯文哲: -0.90 (Negative)
```

### 📈 Trend View
Switch to "Celebrity Trend" to see:
- **Celebrity Selector**: Choose from 10 celebrities
- **Date Range**: Slider for 1-30 days
- **Line Chart**: Sentiment over time with threshold lines
- **Data Table**: Historical records

### 📊 Statistics View
Switch to "Statistics" to see:
- **Key Metrics**: Total records, unique celebrities, averages
- **Pie Chart**: Sentiment distribution (40% positive, 20% neutral, 40% negative)
- **Recent Activity**: Last 10 processed celebrities

---

## Dashboard Navigation

### Sidebar Controls
- **View Mode**: Switch between Rankings, Trends, Statistics
- **Sort Options**: (In Rankings view) Sort by sentiment or date
- **Celebrity Selection**: (In Trend view) Choose celebrity
- **Date Range**: (In Trend view) Adjust time window

### Main Content Area
- **Metrics Cards**: Quick stats at the top
- **Data Tables**: Interactive, sortable tables
- **Charts**: Hover for details, interactive zoom/pan
- **Details**: Expandable sections for more info

---

## Stopping the UI

### Option 1: Terminal
Press `Ctrl+C` in the terminal where Streamlit is running

### Option 2: Command Line
```bash
pkill -f streamlit
```

---

## Collecting More Data

Want to add more celebrities to the dashboard?

### Quick Sample (10 more)
```bash
venv/bin/python scripts/collect_sample_data.py
```

### Custom Batch
```bash
venv/bin/python -c "
from src.data_processing.pipeline import DataPipeline
from src.data_collection.celebrity_manager import CelebrityManager

pipeline = DataPipeline()
celebs = CelebrityManager.load_from_json('config/celebrity_seed_list.json')

# Process 20 celebrities (will take ~3-5 minutes)
summary = pipeline.process_multiple_celebrities(celebs, limit=20)
print(f'Processed {summary[\"successful\"]} celebrities')
"
```

Then refresh the browser to see new data!

---

## Troubleshooting

### Issue: "Address already in use"
**Solution**:
```bash
pkill -f streamlit
./scripts/run_ui.sh
```

### Issue: "No data available"
**Solution**:
```bash
venv/bin/python scripts/collect_sample_data.py
# Then refresh browser
```

### Issue: PostgreSQL not running
**Solution**:
```bash
/opt/homebrew/opt/postgresql@14/bin/postgres \
  -D /opt/homebrew/var/postgresql@14 \
  > logs/postgres.log 2>&1 &
```

### Issue: Charts not showing
**Solution**:
- Clear browser cache
- Try incognito/private mode
- Refresh page (F5 or Cmd+R)

---

## Features to Explore

### 1. Sorting
Click the sort dropdown to view:
- Highest sentiment first (most positive)
- Lowest sentiment first (most negative)
- Most recent updates first

### 2. Celebrity Details
Click any celebrity name in the selectbox to see:
- Full summary text
- Sentiment score and category
- Source link

### 3. Trend Analysis
Select a celebrity with multiple records to see:
- How sentiment changes over time
- Whether they're trending up or down
- Threshold crossings (positive/neutral/negative)

### 4. Distribution Analysis
Check the Statistics view to understand:
- Overall sentiment balance
- Which categories are most represented
- Recent data collection activity

---

## Performance Tips

### For Faster Loading
- Keep data under 100 records initially
- Process celebrities in small batches
- Use the limit parameter when collecting data

### For Better Charts
- Use Chrome or Firefox (best Plotly support)
- Keep browser zoom at 100%
- Use full-screen mode for better visibility

---

## System Requirements

**Verified Working On**:
- ✅ macOS Sonoma 14.x (Apple Silicon)
- ✅ Python 3.13
- ✅ PostgreSQL 14.19
- ✅ Chrome/Firefox/Safari browsers

**Recommended**:
- Screen resolution: 1920x1080 or higher
- RAM: 8GB minimum
- Browser: Latest version of Chrome/Firefox

---

## What the UI Does

### Data Flow
```
PostgreSQL Database
        ↓
  CelebrityDashboard
        ↓
  Streamlit Components
        ↓
   Plotly Charts
        ↓
   Your Browser
```

### Real-Time Updates
- Queries database on each view change
- Always shows latest data
- No caching (for development)

### Interactive Features
- Hover over charts for details
- Click to select celebrities
- Adjust sliders for date ranges
- Sort and filter data

---

## Next Steps After Launch

1. **Explore the Data**
   - Check different celebrities
   - Review sentiment scores
   - Analyze trends

2. **Collect More Data**
   - Process more celebrities
   - Build historical records
   - Track changes over time

3. **Customize Views**
   - Try different sort orders
   - Adjust date ranges
   - Compare celebrities

4. **Monitor System**
   - Check logs for errors
   - Verify data quality
   - Track API usage

---

## Files and Logs

**UI Application**:
- Main file: `src/ui/app.py`
- Launch script: `scripts/run_ui.sh`

**Logs** (if needed):
- PostgreSQL: `logs/postgres.log`
- Streamlit: Output to terminal

**Data Source**:
- Database: `celebrity_index`
- Table: `celebrity_data`

---

## Support

### Debug Tools
```bash
# Check UI is ready
venv/bin/python tests/ui/test_ui_debug.py

# Test UI runtime
venv/bin/python tests/ui/test_ui_runtime.py

# Check database
venv/bin/python tests/unit/test_db_connection.py
```

### Verify Data
```bash
# Count records
/opt/homebrew/opt/postgresql@14/bin/psql -d celebrity_index -c \
  "SELECT COUNT(*), COUNT(DISTINCT name) FROM celebrity_data;"

# View sample
/opt/homebrew/opt/postgresql@14/bin/psql -d celebrity_index -c \
  "SELECT name, sentiment FROM celebrity_data ORDER BY sentiment DESC LIMIT 5;"
```

---

## 🎉 You're Ready!

The Celebrity Index Collector UI is **fully tested and ready to launch**.

Just run:
```bash
./scripts/run_ui.sh
```

And start exploring Taiwan celebrity sentiment data!

---

**Happy Analyzing! 📊✨**
