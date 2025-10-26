from src.data_collection.google_search import GoogleSearchCollector
from src.data_processing.text_cleaner import TextCleaner
from src.data_processing.sentiment_analyzer import SentimentAnalyzer
from src.storage.db_connection import DatabaseConnection
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import psutil
import os

logger = logging.getLogger(__name__)

class DataPipeline:
    def __init__(self):
        self.collector = GoogleSearchCollector()
        self.cleaner = TextCleaner()
        self.analyzer = SentimentAnalyzer()

    @staticmethod
    def get_optimal_workers(max_workers=None):
        """
        Calculate optimal number of worker threads based on system resources.
        Returns a reasonable worker count that won't overwhelm the system.
        """
        if max_workers:
            return max_workers

        try:
            # Get number of CPU cores
            cpu_count = os.cpu_count() or 4

            # Get available memory in GB
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024 ** 3)

            # Conservative: 1 worker per CPU core, but max 8
            # Reduce if memory is limited (< 2GB available)
            base_workers = min(cpu_count, 8)

            if available_gb < 2:
                base_workers = min(base_workers, 2)
            elif available_gb < 4:
                base_workers = min(base_workers, 4)

            logger.info(f"System info: {cpu_count} CPUs, {available_gb:.1f}GB available → {base_workers} workers")
            return base_workers

        except Exception as e:
            logger.warning(f"Could not detect system resources, using 4 workers: {e}")
            return 4

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

    def process_multiple_celebrities(self, celebrity_list, limit=None, max_workers=None, use_parallel=True):
        """
        Process multiple celebrities with optional parallel processing

        Args:
            celebrity_list: List of celebrity names or dicts with 'name' key
            limit: Maximum number to process (None = all)
            max_workers: Number of worker threads (None = auto-detect based on system)
            use_parallel: Enable parallel processing (default: True)

        Returns: dict with summary statistics
        """
        # Prepare celebrity list
        celeb_names = []
        for celeb in celebrity_list:
            name = celeb if isinstance(celeb, str) else celeb.get('name')
            celeb_names.append(name)
            if limit and len(celeb_names) >= limit:
                break

        total_count = len(celeb_names)
        logger.info(f"Processing {total_count} celebrities (parallel={use_parallel}, limit={limit or 'none'})...")

        if not use_parallel or total_count <= 1:
            # Fall back to sequential processing
            return self._process_sequential(celeb_names)

        # Use parallel processing
        return self._process_parallel(celeb_names, max_workers)

    def _process_sequential(self, celeb_names):
        """Process celebrities sequentially"""
        processed = []
        failed = []

        for idx, name in enumerate(celeb_names, 1):
            try:
                logger.info(f"[{idx}/{len(celeb_names)}] Processing {name}...")
                result = self.process_celebrity(name)
                if result:
                    processed.append(result)
                else:
                    failed.append(name)
            except Exception as e:
                logger.error(f"✗ Error processing {name}: {str(e)}")
                failed.append(name)

        return self._build_summary(processed, failed)

    def _process_parallel(self, celeb_names, max_workers=None):
        """Process celebrities in parallel using ThreadPoolExecutor"""
        processed = []
        failed = []

        # Determine optimal worker count
        num_workers = self.get_optimal_workers(max_workers)
        num_workers = min(num_workers, len(celeb_names))

        logger.info(f"Starting parallel processing with {num_workers} workers...")

        try:
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                # Submit all tasks
                future_to_name = {
                    executor.submit(self.process_celebrity, name): name
                    for name in celeb_names
                }

                # Process completed tasks as they finish
                completed = 0
                for future in as_completed(future_to_name):
                    completed += 1
                    name = future_to_name[future]

                    try:
                        result = future.result()
                        if result:
                            processed.append(result)
                        else:
                            failed.append(name)
                        logger.info(f"Progress: [{completed}/{len(celeb_names)}] ✓ {name}")

                    except Exception as e:
                        logger.error(f"Progress: [{completed}/{len(celeb_names)}] ✗ {name}: {str(e)}")
                        failed.append(name)

        except Exception as e:
            logger.error(f"Parallel execution error: {str(e)}, falling back to sequential processing")
            return self._process_sequential(celeb_names)

        return self._build_summary(processed, failed)

    def _build_summary(self, processed, failed):
        """Build processing summary"""
        total = len(processed) + len(failed)
        summary = {
            'total_attempted': total,
            'successful': len(processed),
            'failed': len(failed),
            'success_rate': len(processed) / total * 100 if total > 0 else 0,
            'processed': processed,
            'failed_names': failed
        }

        logger.info(f"✓ Processing complete: {len(processed)}/{total} successful ({summary['success_rate']:.1f}%)")

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
