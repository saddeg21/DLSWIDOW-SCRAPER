"""
Helper functions and utilities.
"""

import re
import html
import unicodedata
from typing import List, Optional, Dict, Any
import json
import csv
import pandas as pd
from pathlib import Path

def clean_text(text: str) -> str:
    """Clean and normalize tweet text."""
    if not text:
        return ""
    
    # Unescape HTML entities
    text = html.unescape(text)
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKC', text)
    
    text = re.sub(r'\s+', ' ', text)
    
    text = text.strip()

    return text


def extract_mentions(text: str) -> List[str]:
    """Extract mentions from tweet text."""
    if not text:
        return []
    
    pattern = r'@([A-Za-z0-9_]+)'
    mentions = re.findall(pattern, text)

    seen = set()
    unique_mentions = []
    for mention in mentions:
        if mention.lower() not in seen:
            seen.add(mention.lower())
            unique_mentions.append(mention)
    
    return unique_mentions

def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from tweet text."""
    if not text:
        return []
    
    pattern = r'#(\w+)'
    hashtags = re.findall(pattern, text)

    seen = set()
    unique_hashtags = []
    for hashtag in hashtags:
        if hashtag.lower() not in seen:
            seen.add(hashtag.lower())
            unique_hashtags.append(hashtag)
    
    return unique_hashtags

def extract_urls(text: str) -> List[str]:
    """Extract URLs from tweet text."""
    if not text:
        return []
    
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)

    return list(set(urls))

def parse_twitter_date(date_str: str) -> Optional[datetime]:
    """Parse Twitter date string to datetime object."""
    from datetime import datetime

    if not date_str:
        return None
    
    formats = [
        '%a %b %d %H:%M:%S %z %Y',  # Wed Oct 05 20:11:50 +0000 2022
        '%Y-%m-%dT%H:%M:%S.%fZ',    # 2022-10-05T20:11:50.000Z
        '%Y-%m-%dT%H:%M:%SZ',       # 2022-10-05T20:11:50Z
        '%Y-%m-%d %H:%M:%S',        # 2022-10-05 20:11:50
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.isoformat()
        except ValueError:
            continue
    
    return None

def parse_number_abbrev(text: str) -> int:
    """Parse abbreviated number strings like '1.2K' to integers."""
    if not text or text == '':
        return 0

    text = text.replace(',', '').strip()

    multipliers = {
        'K': 1000,
        'M': 1000000,
        'B': 1000000000,
        'k': 1000,
        'm': 1000000,
        'b': 1000000000
    }

    for suffix, multiplier in multipliers.items():
        if text.endswith(suffix):
            try:
                number = float(text[:-1])
                return int(number * multiplier)
            except ValueError:
                return 0
    
    try:
        return int(float(text))
    except ValueError:
        return 0

def save_tweets_to_csv(tweets: List[Any], filename: str) -> None:
    """Save a list of Tweet objects to a CSV file."""
    if not tweets:
        return
    
    tweet_dicts = [tweet.to_dict() if hasattr(tweet, 'to_dict') else tweet for tweet in tweets]

    df = pd.DataFrame(tweet_dicts)
    df.to_csv(filename, index=False, encoding='utf-8')

def save_tweets_to_json(tweets: List[Any], filename: str, indent: int = 2) -> None:
    """Save a list of Tweet objects to a JSON file."""
    if not tweets:
        return
    
    tweet_dicts = [tweet.to_dict() if hasattr(tweet, 'to_dict') else tweet for tweet in tweets]

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(tweet_dicts, f, indent=indent, default=str, ensure_ascii=False)

def load_tweets_from_json(filename: str) -> List[Dict[str, Any]]:
    """Load a list of tweets from a JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

def create_filename(username: str, prefix: str = "tweets", extension: str = "csv") -> str:
    """Create a standardized filename for saving tweets."""
    
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_username = re.sub(r'[^\w\-_.]', '', username)
    return f"{prefix}_{clean_username}_{timestamp}.{extension}

def ensure_directory(path: str) -> Path:
    """Ensure that a directory exists."""
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

def get_file_size(filename: str) -> str:
    """Get the size of a file in bytes."""
    try:
        size = Path(filename).stat().st_size

        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    except FileNotFoundError:
        return "0 B"

def validate_twitter_username(username: str) -> bool:
    """Validate a Twitter username."""
    if not username:
        return False
    
    username = username.lstrip('@')

    # Twitter username rules:
    # - 1-15 characters
    # - Letters, numbers, underscores only
    # - Cannot be all numbers
    pattern = r'^[A-Za-z0-9_]{1,15}$'

    # Cannot be all numbers
    if not re.match(pattern, username):
        return False

    return True

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to a maximum length."""
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix

def merge_tweet_lists(*tweet_lists: List[Any]) -> List[Any]:
    """Merge multiple lists of tweets, removing duplicates based on tweet ID."""
    seen_content = set()
    merged = []

    for tweet_list in tweet_lists:
        for tweet in tweet_list:
            content = getattr(tweet, 'content', str(tweet))
            if content not in seen_content:
                seen_content.add(content)
                merged.append(tweet)
    
    return merged