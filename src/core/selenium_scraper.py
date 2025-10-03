"""
Selenium-based scraper implementation.
"""

import time
import random
from typing import List, Dict, Any, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from .base_scraper import BaseScraper, ScrapingError
from ..models.tweet import Tweet
from ..models.user import User
from ..utils.helpers import clean_text, extract_mentions, extract_hashtags
from ..utils.config import Config


class SeleniumScraper(BaseScraper):
    """Selenium-based scraper implementation."""

    def __init__(self, config: Optional[Config] = None):
        super().__init__(config)
        self.driver: Optional[webdriver.Chrome] = None
        self._setup_driver()

    def _setup_driver(self) -> None:
        """Set up the Selenium WebDriver."""
        try:
            chrome_options = Options()

            selenium_config = self.config.get('selenium', {})

            if selenium_config.get('headless', True):
                chrome_options.add_argument("--headless")
            
            window_size = selenium_config.get('window_size', '1920,1080')
            chrome_options.add_argument(f"--window-size={window_size}")

            user_agent = selenium_config.get('user_agent')
            if user_agent:
                chrome_options.add_argument(f'--user-agent={user_agent}')
            
            default_options = [
                "--no-sandbox",
                "--disable-dev-shm-usage", 
                "--disable-gpu",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-images",  # Faster loading
                "--disable-javascript-harmony-shipping",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
            ]

            config_options = selenium_config.get('chrome_options', [])
            all_options = default_options + config_options

            for option in all_options:
                chrome_options.add_argument(option)
            
            prefs = {
                "profile.default_content_setting_values": {
                    "images": 2,  # Block images
                    "plugins": 2,  # Block plugins
                    "popups": 2,  # Block popups
                    "geolocation": 2,  # Block location sharing
                    "notifications": 2,  # Block notifications
                    "media_stream": 2,  # Block media stream
                }
            }
            chrome_options.add_experimental_option('prefs', prefs)

            self.driver = webdriver.Chrome(options=chrome_options)

            implicit_wait = selenium_config.get('implicit_wait', 10)
            page_load_timeout = selenium_config.get('page_load_timeout', 30)

            self.driver.implicitly_wait(implicit_wait)
            self.driver.set_page_load_timeout(page_load_timeout)

            self.logger.info("Selenium WebDriver initialized successfully.")

        except Exception as e:
            self.logger.error(f"Error initializing Selenium WebDriver: {e}")
            raise ScrapingError(f"Failed to initialize WebDriver: {e}")
        

    def scrape_user_tweets(self, username: str, max_tweets: int = 100, include_replies: bool = False, include_retweets: bool = True) -> List[Tweet]:
        username = self.validate_username(username)
        self.logger.info(f"Scraping tweets for user: @{username} (max: {max_tweets})")

        try:
            url = f"https://twitter.com/{username}"
            if not include_replies:
                url += "?f=tweets"

            self.driver.get(url)
            self._wait_for_page_load()

            tweets = []
            scroll_count = 0
            max_scrolls = self.config.get('selenium.max_scrolls', 5)
            scroll_pause = self.config.get('selenium.scroll_pause_time', 3)

            while len(tweets) < max_tweets and scroll_count < max_scrolls:
                tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='tweet']")

                self.logger.debug(f"Found {len(tweet_elements)} tweet elements")

                for tweet_elem in tweet_elements[len(tweets):]:
                    try:
                        tweet = self._extract_tweet_data(tweet_elem, username)

                        if tweet and self._should_include_tweet(tweet, include_replies, include_retweets):
                            tweets.append(tweet)

                            if len(tweets) >= max_tweets:
                                break

                    except Exception as e:
                        self.logger.warning(f"Error extracting tweet data: {e}")
                        continue

                if len(tweets) < max_tweets:
                    self._scroll_page()
                    time.sleep(scroll_pause)
                    scroll_count += 1

            self.logger.info(f"Scraped {len(tweets)} tweets so far...")
            return tweets[:max_tweets]

        except Exception as e:
            self.logger.error(f"Error scraping tweets for user @{username}: {e}")
            raise ScrapingError(f"Failed to scrape tweets for user @{username}: {e}")
    
    def scrape_user_profile(self, username: str) -> Optional[User]:
        username = self.validate_username(username)
        self.logger.info(f"Scraping profile for user: @{username}")

        try:
            url = f"https://twitter.com/{username}"
            self.driver.get(url)
            self._wait_for_page_load()

            profile_data = self._extract_profile_data(username)

            if profile_data:
                user = User(**profile_data)
                self.logger.info(f"Scraped profile for user @{username}")
                return user
            else:
                self.logger.warning(f"No profile data found for user @{username}")
                return None
        
        except Exception as e:
            self.logger.error(f"Error scraping profile for user @{username}: {e}")
            raise ScrapingError(f"Failed to scrape profile for user @{username}: {e}")
    
    def _extract_tweet_data(self, tweet_element, username: str) -> Optional[Tweet]:
        """Extract tweet data from a tweet element."""
        try:
            content_elem = tweet_element.find_element(By.CSS_SELECTOR, "[data-testid='tweetText']")
            content = clean_text(content_elem.text)

            if not content:
                return None
            
            try:
                time_elem = tweet_element.find_element(By.CSS_SELECTOR, "time")
                timestamp_str = time_elem.get_attribute("datetime")
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            except:
                timestamp = datetime.now()
            
            #Engagement metrics
            metrics = self._extract_engagement_metrics(tweet_element)

            mentions = extract_mentions(content)
            hashtags = extract_hashtags(content)

            tweet_data = {
                'id': None,  # Not easily available in web scraping
                'content': content,
                'username': username,
                'timestamp': timestamp,
                'likes': metrics.get('likes', 0),
                'retweets': metrics.get('retweets', 0),
                'replies': metrics.get('replies', 0),
                'quotes': metrics.get('quotes', 0),
                'mentions': mentions,
                'hashtags': hashtags,
                'url': f"https://twitter.com/{username}",
                'method': 'selenium'
            }

            return Tweet(**tweet_data)
        
        except NoSuchElementException as e:
            return None
        except Exception as e:
            self.logger.debug(f"Error extracting tweet data: {e}")
            return None
    
    def _extract_engagement_metrics(self, tweet_element) -> Dict[str, int]:
        """Extract engagement metrics from a tweet element."""
        metrics = {}

        metric_selectors = {
            'replies': "[data-testid='reply']",
            'retweets': "[data-testid='retweet']",
            'likes': "[data-testid='like']",
            'quotes': "[data-testid='quote']"
        }

        for metric, selector in metric_selectors.items():
            try:
                elem = tweet_element.find_element(By.CSS_SELECTOR, selector)
                text = elem.text.strip()

                metrics[metric] = self._parse_metric_number(text)
            except (NoSuchElementException, ValueError):
                metrics[metric] = 0
        
        return metrics

    def _parse_metric_number(self, text: str) -> int:
        """Parse metric numbers like '1.2K' into integers."""
        if not text or text=='':
            return 0
        
        text = text.replace(',', '')

        if 'K' in text:
            return int(float(text.replace('K', '')) * 1000)
        elif 'M' in text:
            return int(float(text.replace('M', '')) * 1_000_000)
        else:
            try:
                return int(text)
            except:
                return 0

    def _extract_profile_data(self, username: str) ->Optional[Dict[str, Any]]:
        """Extract user profile data from the profile page."""
        
        try:
            profile_data = {
                'username': username,
                'display_name': None,
                'bio': None,
                'location': None,
                'website': None,
                'followers_count': 0,
                'following_count': 0,
                'tweet_count': 0,
                'verified': False,
                'profile_image_url': None,
                'banner_image_url': None,
                'created_at': None
            }
            #DISPLAY NAME
            try:
                name_elem = self.driver.find_element(
                    By.CSS_SELECTOR, "[data-testid='UserName'] span"
                )

                profile_data['display_name'] = name_elem.text
            except:
                pass
            
            #BIO
            try:
                bio_elem = self.driver.find_element(
                    By.CSS_SELECTOR, "[data-testid='UserDescription']"
                )
                profile_data['bio'] = clean_text(bio_elem.text)
            except:
                pass
            
            return profile_data
        
        except Exception as e:
            self.logger.debug(f"Error extracting profile data: {e}")
            return None

    ## WILL BE UPDATED LATER    
    def _should_include_tweet(self, tweet: Tweet, include_replies: bool, include_retweets: bool) -> bool:
        return True


    def _wait_for_page_load(self, timeout: int = 10) -> None:
        """Wait for the main content of the page to load."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
        except TimeoutException:
            self.logger.warning("Page load timeout - continuing anyway")
    
    def _scroll_page(self) -> None:
        """Scroll the page to load more content."""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Selenium WebDriver closed successfully.")
            except Exception as e:
                self.logger.error(f"Error closing Selenium WebDriver: {e}")
        super().cleanup()
