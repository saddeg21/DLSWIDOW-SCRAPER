""" Data processing utilities. """

import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from loguru import logger

from ..models.tweet import Tweet
from ..models.user import User


class DataProcessor:
    """Data processing and analysis utilities for scraped data."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    def tweets_to_dataframe(self, tweets: List[Tweet]) -> pd.DataFrame:
        """Convert a list of Tweet objects to a pandas DataFrame."""
        if not tweets:
            return pd.DataFrame()

        tweet_dicts = [tweet.to_dict() for tweet in tweets]

        df = pd.DataFrame(tweet_dicts)

        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        logger.info(f"Converted {len(tweets)} tweets to DataFrame with {len(df.columns)} columns.")
        return df
    
    def users_to_dataframe(self, users: List[User]) -> pd.DataFrame:
        """Convert a list of User objects to a pandas DataFrame."""
        if not users:
            return pd.DataFrame()

        user_dicts = [user.to_dict() for user in users]

        df = pd.DataFrame(user_dicts)

        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        
        logger.info(f"Converted {len(users)} users to DataFrame with {len(df.columns)} columns.")
        return df
    
    def analyze_engagement(self, tweets: List[Tweet]) -> Dict[str, Any]:
        """Analyze engagement metrics from a list of tweets."""
        if not tweets:
            return {}

        df = self.tweets_to_dataframe(tweets)

        analysis = {
            'total_tweets': len(tweets),
            'total_likes': df['likes'].sum(),
            'total_retweets': df['retweets'].sum(),
            'total_replies': df['replies'].sum(),
            'avg_likes': df['likes'].mean(),
            'avg_retweets': df['retweets'].mean(),
            'avg_replies': df['replies'].mean(),
            'max_likes': df['likes'].max(),
            'max_retweets': df['retweets'].max(),
            'max_replies': df['replies'].max(),
            'engagement_rate': (df['likes'] + df['retweets'] + df['replies']).mean()
        }

        # Add most engaged tweet
        if not df.empty:
            engagement_scores = df['likes'] + df['retweets'] + df['replies']
            most_engaging_idx = engagement_scores.idxmax()
            analysis['most_engaging_tweet'] = {
                'text': df.loc[most_engaging_idx, 'text'],
                'likes': df.loc[most_engaging_idx, 'likes'],
                'retweets': df.loc[most_engaging_idx, 'retweets'],
                'replies': df.loc[most_engaging_idx, 'replies'],
                'total_engagement': engagement_scores.iloc[most_engaging_idx]
            }

        logger.info(f"Analyzed engagement for {len(tweets)} tweets")
        return analysis
    
    def extract_hashtags(self, tweets: List[Tweet]) -> Dict[str, int]:
        """Extract and count hashtags from a list of tweets."""
        hashtag_pattern = r'#\w+'
        hashtag_counts = {}

        for tweet in tweets:
            hashtags = re.findall(hashtag_pattern, tweet.text.lower())
            for hashtag in hashtags:
                hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1

        # item 1 because value holded on index 1
        # reverse gives us descending order
        sorted_hashtags = dict(sorted(hashtag_counts.items(), key=lambda item: item[1], reverse=True))
       
        logger.info(f"Extracted {len(sorted_hashtags)} unique hashtags from {len(tweets)} tweets")
        return sorted_hashtags
    
    def extract_mentions(self, tweets: List[Tweet]) -> Dict[str, int]:
        """Extract and count user mentions from a list of tweets."""
        mention_pattern = r'@\w+'
        mention_counts = {}

        for tweet in tweets:
            mentions = re.findall(mention_pattern, tweet.text.lower())
            for mention in mentions:
                mention_counts[mention] = mention_counts.get(mention, 0) + 1

        sorted_mentions = dict(sorted(mention_counts.items(), key=lambda item: item[1], reverse=True))
        
        logger.info(f"Extracted {len(sorted_mentions)} unique mentions from {len(tweets)} tweets")
        return sorted_mentions
    
    def get_posting_patterns(self, tweets: List[Tweet]) -> Dict[str, Any]:
        """Analyze posting patterns from a list of tweets."""
        if not tweets:
            return {}

        df = self.tweets_to_dataframe(tweets)

        df = df[df['timestamp'].notna()]

        if df.empty:
            return {'error': 'No valid timestamps found'}
        
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.day_name()
        df['month'] = df['timestamp'].dt.month_name()

        patterns = {
            'hourly_distribution': df['hour'].value_counts().sort_index().to_dict(),
            'daily_distribution': df['day_of_week'].value_counts().to_dict(),
            'monthly_distribution': df['month'].value_counts().to_dict(),
            'most_active_hour': df['hour'].mode().iloc[0] if not df['hour'].mode().empty else None,
            'most_active_day': df['day_of_week'].mode().iloc[0] if not df['day_of_week'].mode().empty else None,
            'total_days_active': df['timestamp'].dt.date.nunique(),
            'average_tweets_per_day': len(df) / max(df['timestamp'].dt.date.nunique(), 1)
        }
        
        logger.info(f"Analyzed posting patterns for {len(tweets)} tweets")
        return patterns

    def filter_tweets_by_engagement(self, tweets: List[Tweet], min_likes: int = 0, min_retweets: int = 0, min_replies: int = 0) -> List[Tweet]:
        """Filter tweets based on minimum engagement thresholds."""
        filtered_tweets = []

        for tweet in tweets:
            if (tweet.likes >= min_likes and 
                tweet.retweets >= min_retweets and 
                tweet.replies >= min_replies):
                filtered_tweets.append(tweet)
        
        logger.info(f"Filtered {len(filtered_tweets)} tweets from {len(tweets)} based on engagement thresholds")
        return filtered_tweets
    
    def export_to_csv(self, df: pd.DataFrame, filename: str) -> None:
        """Export a DataFrame to a CSV file."""
        try:
            df = self.tweets_to_dataframe(df)
            df.to_csv(filename, index=False)
            logger.info(f"Exported {len(tweets)} tweets to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to export tweets to CSV: {e}")
            return False
    
    def export_to_json(self, tweets: List[Tweet], filename: str) -> bool:
        """Export a list of tweets to a JSON file."""
        try:
            tweet_dicts = [tweet.to_dict() for tweet in tweets]
            df = pd.DataFrame(tweet_dicts)
            df.to_json(filename, orient='records', indent=2, date_format='iso')
            logger.info(f"Exported {len(tweets)} tweets to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to export tweets to JSON: {e}")
            return False

    def sentiment_analysis_placeholder(self, tweets: List[Tweet]) -> Dict[str, Any]:
        """Placeholder for sentiment analysis on tweets."""
        # This is a placeholder function. In a real implementation, you would integrate
        # with a sentiment analysis library or API.
        
        total_chars = sum(len(tweet.text) for tweet in tweets)
        avg_length = total_chars / len(tweets) if tweets else 0

        positive_keywords = ['good', 'great', 'excellent', 'amazing', 'love', 'happy']
        negative_keywords = ['bad', 'terrible', 'hate', 'awful', 'sad', 'angry']
        
        positive_count = 0
        negative_count = 0

        for tweet in tweets:
            text_lower = tweet.text.lower()
            if any(keyword in text_lower for keyword in positive_keywords):
                positive_count += 1
            if any(keyword in text_lower for keyword in negative_keywords):
                negative_count += 1
        
        return {
            'total_tweets': len(tweets),
            'average_length': avg_length,
            'positive_indicators': positive_count,
            'negative_indicators': negative_count,
            'neutral': len(tweets) - positive_count - negative_count,
            'note': 'This is a basic analysis. Integrate with NLP libraries for advanced sentiment analysis.'
        }