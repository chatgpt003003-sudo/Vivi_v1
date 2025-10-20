-- Celebrity Sentiment Data Table (Simplified)
CREATE TABLE IF NOT EXISTS celebrity_data (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    cleaned_paragraph TEXT,
    source TEXT,
    sentiment DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster queries by celebrity name
CREATE INDEX idx_celebrity_name ON celebrity_data(name);

-- Index for sentiment scores
CREATE INDEX idx_sentiment ON celebrity_data(sentiment);

-- Index for created_at for time-based queries
CREATE INDEX idx_created_at ON celebrity_data(created_at);
