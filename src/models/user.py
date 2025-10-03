"""
This module contains the User model, which represents a Twitter user
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
import json

@dataclass
class User:
    """
    A class representing a Twitter user.

    Attributes:
        username: Twitter username (without @)
        display_name: Display name shown on profile
        bio: User bio/description
        location: User location
        website: User website URL
        followers_count: Number of followers
        following_count: Number of accounts following
        tweet_count: Number of tweets posted
        verified: Whether the account is verified
        profile_image_url: URL to profile image
        banner_image_url: URL to banner image
        created_at: Account creation date
        metadata: Additional metadata
    """

    username: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    followers_count: int = 0
    following_count: int = 0
    tweet_count: int = 0
    verified: bool = False
    profile_image_url: Optional[str] = None
    banner_image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """
        Post-initialization processing to adjust username and metadata
        """
        if self.username:
            self.username = self.username.lstrip("@").strip()
        
        if self.metadata is None:
            self.metadata = {}
        
    @property
    def profile_url(self) -> str:
        """
        Returns the URL to the user's Twitter profile.
        """
        return f"https://twitter.com/{self.username}"
    
    @property
    def follower_to_following_ratio(self) -> float:
        """
        Returns the ratio of followers to following.
        """
        if self.following_count == 0:
            return float('inf') if self.followers_count > 0 else 0
        return self.followers_count / self.following_count
    
    @property
    def tweets_per_day(self) -> float:
        """
        Returns the average number of tweets per day since account creation.
        """
        if not self.created_at or self.tweet_count == 0:
            return 0.0

        days_since_creation = (datetime.now() - self.created_at).days
        if days_since_creation == 0:
            return self.tweet_count

        return self.tweet_count / days_since_creation
    
    @property
    def account_age_days(self) -> int:
        """
        Returns the age of the account in days.
        """
        if not self.created_at:
            return 0
        return (datetime.now() - self.created_at).days
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the User object to a dictionary representation.
        """
        return {
            "username": self.username,
            "display_name": self.display_name,
            "bio": self.bio,
            "location": self.location,
            "website": self.website,
            "followers_count": self.followers_count,
            "following_count": self.following_count,
            "tweet_count": self.tweet_count,
            "verified": self.verified,
            "profile_image_url": self.profile_image_url,
            "banner_image_url": self.banner_image_url,
            "created_at": self.created_at,
            "profile_url": self.profile_url,
            "tweets_per_day": self.tweets_per_day,
            "account_age_days": self.account_age_days,
            "follower_to_following_ratio": self.follower_to_following_ratio,
            "metadata": self.metadata,
        }
    
    def to_json(self, indent: Optional[int] = None) -> str:
        """
        Converts the User object to a JSON string representation.
        """
        user_dict = self.to_dict()
        return json.dumps(user_dict, indent=indent, default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """
        Creates a User object from a dictionary representation.
        """
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except:
                created_at = None
        
        elif not isinstance(created_at, datetime):
            created_at = None

        return cls(
            username=data.get('username', ''),
            display_name=data.get('display_name'),
            bio=data.get('bio'),
            location=data.get('location'),
            website=data.get('website'),
            followers_count=data.get('followers_count', 0),
            following_count=data.get('following_count', 0),
            tweet_count=data.get('tweet_count', 0),
            verified=data.get('verified', False),
            profile_image_url=data.get('profile_image_url'),
            banner_image_url=data.get('banner_image_url'),
            created_at=created_at,
            metadata=data.get('metadata', {})
        )

    @classmethod
    def from_json(cls, json_str: str) -> "User":
        """
        Creates a User object from a JSON string representation.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __str__(self) -> str:
        """
        Returns a string representation of the User object.
        """
        display = self.display_name or self.username
        return f"User(@{self.username} - {display}, bio={self.bio})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"User(username='{self.username}', followers={self.followers_count}, verified={self.verified})"