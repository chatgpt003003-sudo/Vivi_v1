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

    def process_celebrity(self, celebrity_name, num_results=10):
        """
        Complete pipeline for one celebrity:
        1. Collect search results
        2. Clean text
        3. Analyze sentiment
        4. Store in database

        Returns: dict with processing results or None if failed
        """
        logger.info(f"Processing {celebrity_name}...")

        # Step 1: Collect data
        search_results = self.collector.search_celebrity(celebrity_name, num_results)
        if not search_results:
            logger.warning(f"⚠ No results for {celebrity_name}")
            return None

        # Step 2: Clean text
        cleaned_text = self.cleaner.clean_search_results(search_results)
        if not cleaned_text:
            logger.warning(f"⚠ No cleaned text for {celebrity_name}")
            return None

        # Step 3: Analyze sentiment
        sentiment_score = self.analyzer.analyze_sentiment(cleaned_text)

        # Get source link
        source = search_results[0]['link'] if search_results else None

        # Step 4: Store results
        record_id = self._store_data(
            name=celebrity_name,
            cleaned_paragraph=cleaned_text,
            source=source,
            sentiment=sentiment_score
        )

        if record_id:
            logger.info(f"✓ {celebrity_name}: sentiment={sentiment_score:.2f}, mentions={len(search_results)}, record_id={record_id}")
            return {
                'record_id': record_id,
                'name': celebrity_name,
                'sentiment': sentiment_score,
                'mention_count': len(search_results),
                'cleaned_text': cleaned_text,
                'source': source
            }
        else:
            logger.error(f"✗ Failed to store data for {celebrity_name}")
            return None

    def _store_data(self, name, cleaned_paragraph, source, sentiment):
        """Store data in database, returns record ID or None"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO celebrity_data (name, cleaned_paragraph, source, sentiment)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (name, cleaned_paragraph, source, sentiment))

            record_id = cursor.fetchone()[0]
            conn.commit()

            logger.info(f"✓ Data stored for {name} (ID: {record_id})")
            return record_id

        except Exception as e:
            conn.rollback()
            logger.error(f"✗ Database error for {name}: {str(e)}")
            return None
        finally:
            cursor.close()
            DatabaseConnection.return_connection(conn)

    def process_multiple_celebrities(self, celebrity_list, limit=None):
        """
        Process multiple celebrities
        celebrity_list: List of celebrity names or dicts with 'name' key
        limit: Maximum number to process (None = all)

        Returns: dict with summary statistics
        """
        logger.info(f"Processing multiple celebrities (limit: {limit or 'none'})...")

        processed = []
        failed = []
        count = 0

        for celeb in celebrity_list:
            # Handle both string names and dict format
            name = celeb if isinstance(celeb, str) else celeb.get('name')

            if limit and count >= limit:
                logger.info(f"Reached limit of {limit} celebrities")
                break

            try:
                result = self.process_celebrity(name)
                if result:
                    processed.append(result)
                else:
                    failed.append(name)

                count += 1

            except Exception as e:
                logger.error(f"✗ Error processing {name}: {str(e)}")
                failed.append(name)

        summary = {
            'total_attempted': count,
            'successful': len(processed),
            'failed': len(failed),
            'success_rate': len(processed) / count * 100 if count > 0 else 0,
            'processed': processed,
            'failed_names': failed
        }

        logger.info(f"✓ Processing complete: {len(processed)}/{count} successful ({summary['success_rate']:.1f}%)")

        return summary

    def get_recent_data(self, limit=10):
        """Retrieve most recent processed data from database"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, name, sentiment, created_at, cleaned_paragraph
                FROM celebrity_data
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))

            results = cursor.fetchall()
            cursor.close()
            DatabaseConnection.return_connection(conn)

            return [{
                'id': row[0],
                'name': row[1],
                'sentiment': float(row[2]),
                'created_at': row[3],
                'text_preview': row[4][:100] if row[4] else None
            } for row in results]

        except Exception as e:
            logger.error(f"✗ Error retrieving data: {str(e)}")
            cursor.close()
            DatabaseConnection.return_connection(conn)
            return []
