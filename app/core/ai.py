from typing import List, Optional, Dict, Any
import openai
from openai import OpenAI
import tiktoken
import logging
import time
from .config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def count_tokens(text: str) -> int:
    """Count the number of tokens in a text string."""
    try:
        encoding = tiktoken.encoding_for_model(settings.OPENAI_MODEL)
        return len(encoding.encode(text))
    except Exception as e:
        logger.warning(f"Error counting tokens: {str(e)}")
        # Fallback: rough estimate
        return len(text.split()) * 1.3

class AIService:
    def __init__(self):
        self.client = client
        self.max_retries = 3
        self.retry_delay = 1  # seconds
    
    async def generate_blog_content(
        self,
        industry: str,
        location: str,
        topic: str,
        style: Optional[str] = "professional",
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate blog content using OpenAI's API with retry logic.
        
        Args:
            industry: The business industry
            location: The geographical location
            topic: The blog topic
            style: Writing style (default: professional)
            max_tokens: Maximum tokens for response
            
        Returns:
            Dict containing generated content and metadata
        """
        prompt = self._create_blog_prompt(industry, location, topic, style)
        
        for attempt in range(self.max_retries):
            try:
                response = await self._make_completion_request(prompt, max_tokens)
                return {
                    "content": response.choices[0].message.content,
                    "tokens_used": response.usage.total_tokens,
                    "finish_reason": response.choices[0].finish_reason
                }
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to generate blog content after {self.max_retries} attempts: {str(e)}")
                    raise
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                time.sleep(self.retry_delay * (attempt + 1))
    
    async def _make_completion_request(self, prompt: str, max_tokens: Optional[int] = None):
        """Make the actual API request to OpenAI."""
        return await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens or settings.MAX_TOKENS,
            temperature=0.7,
            presence_penalty=0.3,
            frequency_penalty=0.3
        )
    
    def _create_blog_prompt(
        self,
        industry: str,
        location: str,
        topic: str,
        style: str
    ) -> str:
        """Create a detailed prompt for blog generation."""
        return f"""
        Create a detailed blog post for a {industry} business in {location}.
        Topic: {topic}
        Style: {style}
        
        The blog post should:
        1. Be locally relevant to {location}
        2. Include industry-specific insights for {industry}
        3. Be SEO-friendly with appropriate headings
        4. Include practical examples and actionable advice
        5. Maintain a {style} tone throughout
        
        Please structure the post with:
        - An engaging introduction
        - 3-4 main sections with subheadings
        - Practical examples or case studies
        - A clear conclusion with call-to-action
        """
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for setting the AI's role and constraints."""
        return """
        You are an expert content writer specializing in local business blogging.
        Your writing is:
        1. Professional and authoritative
        2. Locally relevant and specific
        3. SEO-optimized
        4. Engaging and actionable
        5. Well-structured with clear headings
        
        Always include:
        - Local statistics or references when possible
        - Industry-specific insights
        - Practical examples
        - Clear calls-to-action
        """

# Global AI service instance
ai_service = AIService() 