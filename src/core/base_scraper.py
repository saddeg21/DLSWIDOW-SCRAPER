"""
Abstract base class definition for all scrapers. (ileride Twipy ile genişletiriz)
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import time
import random
from ..models.tweet import Tweet
from ..models.user import User
from ..utils.config import Config
from ..utils.logger import get_logger


class ScrapingError(Exception):
    """Custom exception for scraping-related errors."""
    pass

class BaseScraper(ABC):
    """Abstract base class for all scrapers."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.logger = get_logger(self.__class__.__name__)
        self._setup()
    
    def _setup(self) -> None:
        self.logger.info(f"Initializing {self.__class__.__name__}")
    
    @abstractmethod
    def scrape_user_tweets(self, username: str, max_tweets: int = 100, **kwargs) -> List[Tweet]:
        """Scrape tweets from a specific user."""
        pass
    
    @abstractmethod
    def scrape_user_profile(self, username: str) -> User:
        """Scrape user profile information."""
        pass
    
    def scrape_search_results(self, query: str, max_tweets: int = 100, **kwargs) -> List[Tweet]:
        """Scrape tweets based on a search query."""
        self.logger.warning(f"{self.__class__.__name__} does not implement search scraping")
        pass
    
    def _rate_limit_delay(self) -> None:
        """Introduce a random delay to respect rate limits."""
        if self.config.get('rate_limiting.enabled', True):
            delay = self.config.get('rate_limiting.delay_between_requests',1)
            jitter = random.uniform(0.5, 1.5)
            time.sleep(delay * jitter)

    def _retry_with_backoff(self, func, max_retries: int = 3, *args, **kwargs):
        """Retry a function with exponential backoff."""
        last_exception = None

        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    delay = (2 ** attempt) * random.uniform(1, 2)
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed with error: {e}. Retrying in {delay:.2f} seconds..."
                    )
                    time.sleep(delay)
                else:
                    self.logger.error(f"All {max_retries} attempts failed.")
            
        raise last_exception

    
    def validate_username(self, username: str) -> bool:
        """Validate the format of a Twitter username."""
        if not username:
            raise ValueError("Username cannot be empty")
        
        username = username.lstrip('@')

        if not username.replace("_", "").replace("-","").isalnum():
            raise ValueError("Username can only contain letters, numbers, and underscores")
        
        return username
    
    def cleanup(self) -> None:
        """Cleanup resources."""
        self.logger.info(f"Cleaning up {self.__class__.__name__}")
    
# Not implemented yet

class ScrapingError(Exception):
    """Custom exception for scraping errors."""
    pass

class RateLimiterror(ScrapingError):
    """Exception raised when rate limit is exceeded."""
    pass

class AuthenticationError(ScrapingError):
    """Exception raised for authentication errors."""
    pass