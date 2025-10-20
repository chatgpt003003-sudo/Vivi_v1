from googleapiclient.discovery import build
from config.api_config import GOOGLE_API_KEY, GOOGLE_SEARCH_ENGINE_ID
import logging
from datetime import datetime, timedelta
import time

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

            # Add delay to respect rate limits
            time.sleep(self.rate_limit_delay)

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

            # Add delay to respect rate limits
            time.sleep(self.rate_limit_delay)

            return int(total)
        except Exception as e:
            logger.error(f"✗ Error getting mention count: {str(e)}")
            return 0
