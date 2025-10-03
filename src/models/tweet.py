"""
This module contains the Tweet model, which represents a tweet
and its associated metadata.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

@dataclass
class Tweet:
    """A class representing a tweet and its metadata."""
    content: str
    username: str
    timestamp: datetime
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    quotes: int = 0
    # Prevent from each object sharing the same list instance
    mentions: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    url: str = ""
    method: str = "unknown"
    id: Optional[str] = None
    language: Optional[str] = None
    is_reply: bool = False
    is_retweet: bool = False
    media_urls: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization processing."""
        if self.mentions is None:
            self.mentions = []
        if self.hashtags is None:
            self.hashtags = []
        if self.media_urls is None:
            self.media_urls = []
        if self.metadata is None:
            self.metadata = {}

        ## Clean strip from content
        if self.content:
            self.content = self.content.strip()
    
    @property
    def engagement_total(self) -> int:
        """Calculate total engagement (likes + retweets + replies + quotes)."""
        return self.likes + self.retweets + self.replies + self.quotes
    
    @property
    def has_media(self) -> bool:
        """Check if the tweet contains media."""
        return len(self.media_urls) > 0
    
    @property
    def word_count(self) -> int:
        """Count the number of words in the tweet content."""
        return len(self.content.split()) if self.content else 0
    
    @property
    def character_count(self) -> int:
        """Count the number of characters in the tweet content."""
        return len(self.content) if self.content else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the Tweet object to a dictionary."""
        return {
            "content": self.content,
            "username": self.username,
            "timestamp": self.timestamp.isoformat(),
            "likes": self.likes,
            "retweets": self.retweets,
            "replies": self.replies,
            "quotes": self.quotes,
            "mentions": self.mentions,
            "hashtags": self.hashtags,
            "url": self.url,
            "method": self.method,
            "id": self.id,
            "language": self.language,
            "is_reply": self.is_reply,
            "is_retweet": self.is_retweet,
            "media_urls": self.media_urls,
            'engagement_total' : self.engagement_total,
            'has_media' : self.has_media,
            'word_count' : self.word_count,
            'character_count' : self.character_count,
            "metadata": self.metadata,
        }
    
    def to_json(self, indent: Optional[int] = None) -> str:
        """Convert the Tweet object to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Tweet':
        """Create a Tweet object from a dictionary."""
        data = data.copy()
        
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                timestamp = datetime.now()
        elif not isinstance(timestamp, datetime):
            timestamp = datetime.now()

        return cls(
            id=data.get('id'),
            content=data.get('content', ''),
            username=data.get('username', ''),
            timestamp=timestamp,
            likes=data.get('likes', 0),
            retweets=data.get('retweets', 0),
            replies=data.get('replies', 0),
            quotes=data.get('quotes', 0),
            mentions=data.get('mentions', []),
            hashtags=data.get('hashtags', []),
            url=data.get('url', ''),
            method=data.get('method', 'unknown'),
            language=data.get('language'),
            is_reply=data.get('is_reply', False),
            is_retweet=data.get('is_retweet', False),
            media_urls=data.get('media_urls', []),
            metadata=data.get('metadata', {})
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'Tweet':
        """Create a Tweet object from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    

    def __str__(self) -> str:
        """String representation of the Tweet object."""
        return f"Tweet by @{self.username} at {self.timestamp}: {self.content[:50]}..."
    
    def __repr__(self) -> str:
        """Detailed string representation of the Tweet object."""
        return (f"Tweet(id={self.id}, username={self.username}, timestamp={self.timestamp}, "
                f"likes={self.likes}, retweets={self.retweets}, replies={self.replies}, "
                f"quotes={self.quotes}, mentions={self.mentions}, hashtags={self.hashtags}, "
                f"url={self.url}, method={self.method}, language={self.language}, "
                f"is_reply={self.is_reply}, is_retweet={self.is_retweet}, "
                f"media_urls={self.media_urls}, metadata={self.metadata})")