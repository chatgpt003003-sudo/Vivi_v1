import logging
import google.generativeai as genai
from config.api_config import GEMINI_API_KEY
import re

logger = logging.getLogger(__name__)
genai.configure(api_key=GEMINI_API_KEY)

class SentimentAnalyzer:
    def __init__(self):
        # Using Gemini 2.5 Flash (fast and efficient)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def analyze_sentiment(self, text):
        """
        Analyze sentiment of text
        Returns: Score from -1.0 (very negative) to 1.0 (very positive)
        """
        if not text:
            logger.warning("No text provided for sentiment analysis")
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
            numbers = re.findall(r'-?\d+\.?\d*', score_text)
            if numbers:
                score = float(numbers[0])
                # Clamp between -1 and 1
                score = max(-1.0, min(1.0, score))
                logger.info(f"✓ Sentiment score: {score:.2f}")
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

    def analyze_with_explanation(self, text):
        """
        Analyze sentiment with explanation
        Returns: (score, explanation)
        """
        if not text:
            return 0.0, "No text provided"

        prompt = f"""請分析以下文字的情感傾向，並提供簡短解釋。

        文字內容：
        {text}

        請以下列格式回覆：
        分數：[數字]
        解釋：[簡短說明]

        分數範圍：-1.0（非常負面）到 1.0（非常正面）"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Extract score
            score_match = re.search(r'分數[：:]\s*(-?\d+\.?\d*)', response_text)
            score = 0.0
            if score_match:
                score = float(score_match.group(1))
                score = max(-1.0, min(1.0, score))

            # Extract explanation
            explanation_match = re.search(r'解釋[：:]\s*(.+)', response_text, re.DOTALL)
            explanation = explanation_match.group(1).strip() if explanation_match else response_text

            logger.info(f"✓ Sentiment: {score:.2f} - {explanation[:50]}...")
            return score, explanation

        except Exception as e:
            logger.error(f"✗ Sentiment analysis error: {str(e)}")
            return 0.0, "Analysis failed"
