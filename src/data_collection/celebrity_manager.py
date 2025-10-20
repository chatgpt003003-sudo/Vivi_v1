"""
Celebrity Manager - Simplified version
Manages the list of celebrities to track without a separate celebrities table
"""
from src.data_collection.google_search import GoogleSearchCollector
import logging
import json

logger = logging.getLogger(__name__)

class CelebrityManager:
    def __init__(self, mention_threshold=100):
        self.collector = GoogleSearchCollector()
        self.mention_threshold = mention_threshold

    def validate_celebrity(self, name):
        """
        Check if celebrity meets mention threshold
        Returns: (is_valid, mention_count)
        """
        mention_count = self.collector.get_total_mentions(name)

        if mention_count >= self.mention_threshold:
            logger.info(f"✓ {name}: {mention_count:,} mentions (threshold: {self.mention_threshold:,})")
            return True, mention_count
        else:
            logger.info(f"✗ {name}: {mention_count:,} mentions (below threshold: {self.mention_threshold:,})")
            return False, mention_count

    def validate_batch(self, celebrity_list):
        """
        Validate a list of celebrities
        celebrity_list: List of celebrity names or dicts with 'name' key
        Returns: List of valid celebrities with their mention counts
        """
        validated = []

        for celeb in celebrity_list:
            # Handle both string names and dict format
            name = celeb if isinstance(celeb, str) else celeb.get('name')

            is_valid, mentions = self.validate_celebrity(name)

            if is_valid:
                validated.append({
                    'name': name,
                    'mention_count': mentions
                })

        logger.info(f"✓ Validation complete: {len(validated)}/{len(celebrity_list)} celebrities passed")
        return validated

    @staticmethod
    def load_from_json(filepath):
        """Load celebrity list from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('celebrities', [])

    @staticmethod
    def save_to_json(celebrity_list, filepath):
        """Save celebrity list to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({'celebrities': celebrity_list}, f, ensure_ascii=False, indent=2)
        logger.info(f"✓ Saved {len(celebrity_list)} celebrities to {filepath}")
