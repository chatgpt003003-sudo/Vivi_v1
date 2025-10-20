1# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Celebrity Index Collector is a data collection and sentiment analysis system for quantifying celebrity impact in Taiwan. Test 1 focuses on establishing basic data collection and sentiment analysis capabilities using Google Search API and Google Gemini API for 100 celebrities with daily updates.

## System Architecture

### Data Flow Pipeline
```
Google Search API → Raw Data Collection → Google Gemini Text Cleaning → Sentiment Analysis → PostgreSQL Storage → Desktop UI
```

### Core Components
1. **Data Collection Module**: Google Search API integration for last 24 hours of celebrity mentions
2. **Data Processing Pipeline**: Google Gemini API for text cleaning, followed by sentiment analysis
3. **Celebrity Management**: Reverse discovery approach - find celebrities mentioned online, filter by mention threshold
4. **Data Storage**: PostgreSQL local deployment with sentiment scores and processed text
5. **Desktop UI**: View-only interface for professionals showing rankings and sentiment scores

## Technology Stack

**Backend**: Python
**Database**: PostgreSQL (local deployment)
**APIs**:
- Google Search API (data collection)
- Google Gemini API (text processing)

**Frontend**: Desktop application using Python (Tkinter, PyQt, or Streamlit)

## Database Schema

### Celebrities Table
- `id`, `name`, `category`, `mention_count`, `status`, `created_at`, `updated_at`

### Daily Sentiment Data
- `id`, `celebrity_id` (FK), `collection_date`, `sentiment_score`, `mention_count`, `processed_text`, `raw_data_summary`

## Development Commands

When implemented, common commands will include:
- Database setup and migrations
- API credential configuration
- Daily data collection job
- Sentiment analysis processing
- Desktop UI launch

## Critical Development Protocol

**Test at each step before proceeding**:
1. Implement feature/component
2. Write and run unit tests
3. Report any bugs or issues immediately
4. Fix bugs before proceeding to next step
5. Document fixes and lessons learned

This prevents cascading issues in the data pipeline.

## Compliance & Ethics

- **Respect API Rate Limits**: Honor Google Search API quotas
- **Blacklist Management**: Maintain list of non-crawlable sources
- **Data Minimization**: Collect only necessary public information
- **Privacy**: Focus on public mentions only, no personal data collection

## Implementation Phases

1. **Setup & Configuration**: API credentials, PostgreSQL initialization, schema design
2. **Data Collection**: Google Search API crawler, celebrity discovery, daily scheduling
3. **Data Processing**: Gemini integration, sentiment analysis pipeline, validation
4. **Storage & Management**: PostgreSQL implementation, celebrity management system
5. **UI Development**: Desktop interface with ranking display
6. **Testing & Validation**: Unit/integration testing, data quality validation

## Project Goals

- Collect data for 100 celebrities daily
- Automated text cleaning and sentiment analysis
- Reliable PostgreSQL storage and retrieval
- Functional desktop UI showing sentiment rankings
- Accurate celebrity filtering and discovery
