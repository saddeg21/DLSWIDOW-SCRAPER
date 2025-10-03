"""
Config management module
"""

import os
import yaml
from typing import Any, Dict, Optional
from pathlib import Path

class Config:
    """Configuration management class."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Config class."""

        self._config: Dict[str, Any] = {}
        self._load_config(config_path)
        self._load_env_variables()

    def _load_config(self, config_path: Optional[str] = None) -> None:
        """Load config from YAML file."""
        if config_path is None:
            current_dir = Path(__file__).parent.parent.parent
            config_path = current_dir / "config" / "settings.yaml"

        try:
            if Path(config_path).exists():
                with open(config_path, "r", encoding="utf-8") as file:
                    self._config = yaml.safe_load(file) or {}
            else:
                self._config = self._get_default_config()
        except Exception as e:
            print(f"Error loading config file {config_path}: {e}")
            self._config = self._get_default_config()


    def _load_env_variables(self) -> None:
        """Load environment variables into config."""
        env_mappings = {
            #'TWITTER_BEARER_TOKEN': 'twitter_api.bearer_token',
            #'TWITTER_CONSUMER_KEY': 'twitter_api.consumer_key',
            #'TWITTER_CONSUMER_SECRET': 'twitter_api.consumer_secret',
            #'TWITTER_ACCESS_TOKEN': 'twitter_api.access_token',
            #'TWITTER_ACCESS_TOKEN_SECRET': 'twitter_api.access_token_secret',
            
            # Selenium settings
            'SELENIUM_HEADLESS': 'selenium.headless',
            'SELENIUM_TIMEOUT': 'selenium.page_load_timeout',
            'SELENIUM_IMPLICIT_WAIT': 'selenium.implicit_wait',
            
            # General settings
            'LOG_LEVEL': 'logging.level',
            'RATE_LIMIT_REQUESTS_PER_MINUTE': 'rate_limiting.requests_per_minute',
        }

        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                if value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                elif self._is_float(value):
                    value = float(value)
                
                self._set_nested_value(config_path, value)

    def _is_float(self, value: str) -> bool:
        """Check if a string can be converted to float."""
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _set_nested_value(self, path: str, value: Any) -> None:
        """Set a value in a nested dictionary given a dot-separated path."""
        keys = path.split('.')
        current = self._config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value

    def _get_default_config(self) -> Dict[str, Any]:
        """Return the default configuration."""
        return {
            'defaults': {
                'max_tweets': 100,
                'timeout': 30,
                'retry_attempts': 3,
                'delay_between_requests': 2
            },
            'selenium': {
                'headless': True,
                'window_size': '1920,1080',
                'implicit_wait': 10,
                'page_load_timeout': 30,
                'max_scrolls': 5,
                'scroll_pause_time': 3
            },
            'rate_limiting': {
                'enabled': True,
                'requests_per_minute': 60,
                'delay_between_requests': 1
            },
            'logging': {
                'level': 'INFO'
            },
            'export': {
                'formats': ['csv', 'json'],
                'include_metadata': True
            }
        }
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get a configuration value by dot-separated path."""
        keys = path.split('.')
        current = self._config

        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value by dot-separated path."""
        self._set_nested_value(key, value)
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get a whole section of the configuration."""
        return self._config.get(section, {})
    
    def has(self, key: str) -> bool:
        """Check if a configuration key exists."""
        return self.get(key) is not None

    def update(self, updates: Dict[str, Any]) -> None:
        """Update the configuration with a dictionary of updates."""
        def deep_update(base: Dict, updates: Dict) -> Dict:
            for k, v in updates.items():
                if isinstance(v, dict) and k in base and isinstance(base[k], dict):
                    deep_update(base[k], v)
                else:
                    base[k] = v
            return base
    
    def to_dict(self) -> Dict[str, Any]:
        """Return the entire configuration as a dictionary."""
        return self._config.copy()
    
    def __str__(self) -> str:
        """String representation of the configuration."""
        return f"Config({len(self._config)} sections)"
    
    def __repr__(self) -> str:
        """Detailed string representation of the configuration."""
        return f"Config(sections={list(self._config.keys())})"
