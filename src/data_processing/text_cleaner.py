import google.generativeai as genai
from config.api_config import GEMINI_API_KEY
import logging

logger = logging.getLogger(__name__)

genai.configure(api_key=GEMINI_API_KEY)

class TextCleaner:
    def __init__(self):
        # Using Gemini 2.5 Flash (fast and efficient)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def clean_search_results(self, search_results):
        """
        Clean and summarize search results
        search_results: List of dicts with 'title', 'snippet', 'link'
        Returns: Cleaned text summary
        """
        if not search_results:
            logger.warning("No search results to clean")
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
            fallback_text = combined_text[:500]
            logger.warning(f"Using fallback text ({len(fallback_text)} chars)")
            return fallback_text

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
            logger.info(f"✓ Extracted {len(key_points)} key points")
            return key_points
        except Exception as e:
            logger.error(f"✗ Key point extraction error: {str(e)}")
            return []

    def clean_text_simple(self, text):
        """
        Simple text cleaning without API call
        Removes extra whitespace, special characters, etc.
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = ' '.join(text.split())

        # Remove common ads/promotional text patterns
        ad_patterns = ['點擊', '訂閱', '廣告', '贊助']
        for pattern in ad_patterns:
            text = text.replace(pattern, '')

        return text.strip()
