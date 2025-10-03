# DLS Widow Scraper 🐦

A robust and configurable social media scraper built with Python and Selenium. This tool allows you to extract tweets, user profiles, and engagement metrics from Twitter with support for multiple scraping methods.

## 🚀 Features

- **Selenium-based scraping**: Reliable web scraping using Chrome WebDriver
- **User tweet extraction**: Scrape tweets from specific users with engagement metrics
- **User profile scraping**: Extract complete user profile information
- **Data processing**: Built-in data cleaning and analysis utilities
- **Configurable**: YAML-based configuration for easy customization
- **Logging**: Comprehensive logging with configurable levels
- **Rate limiting**: Built-in delays and retry mechanisms to respect platform limits

## 📁 Project Structure

```
dlswidow-scraper/
├── config/
│   ├── logging.yaml          # Logging configuration
│   └── settings.yaml         # Main application settings
├── src/
│   ├── core/
│   │   ├── base_scraper.py   # Abstract base scraper class
│   │   ├── selenium_scraper.py # Selenium implementation
│   │   └── data_processor.py # Data processing utilities
│   ├── models/
│   │   ├── tweet.py          # Tweet data model
│   │   └── user.py           # User data model
│   └── utils/
│       ├── config.py         # Configuration management
│       ├── helpers.py        # Utility functions
│       └── logger.py         # Logging utilities
├── data/                     # Output directory for scraped data
├── logs/                     # Log files directory
└── requirements.txt          # Python dependencies
```

## 🛠️ Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/dlswidow-scraper.git
   cd dlswidow-scraper
   ```

2. **Create a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Chrome WebDriver**:
   - Download ChromeDriver from [here](https://chromedriver.chromium.org/)
   - Make sure it's in your PATH or specify the path in configuration

## ⚙️ Configuration

Edit `config/settings.yaml` to customize scraping behavior:

```yaml
selenium:
  headless: true
  window_size: "1920,1080"
  max_scrolls: 5
  scroll_pause_time: 3

defaults:
  max_tweets: 100
  timeout: 30
  retry_attempts: 3
```

## 🚀 Usage

### Basic Usage

```python
from src.core.selenium_scraper import SeleniumScraper
from src.utils.config import Config

# Initialize scraper with configuration
config = Config()
scraper = SeleniumScraper(config)

# Scrape user tweets
tweets = scraper.scrape_user_tweets("username", max_tweets=50)

# Scrape user profile
user_profile = scraper.scrape_user_profile("username")

# Clean up
scraper.cleanup()
```

### Data Processing

```python
from src.core.data_processor import DataProcessor

processor = DataProcessor()

# Convert tweets to DataFrame
df = processor.tweets_to_dataframe(tweets)

# Analyze engagement
engagement_stats = processor.analyze_engagement(tweets)
```

## 📊 Data Models

### Tweet Model

- `content`: Tweet text content
- `username`: Author username
- `timestamp`: Tweet timestamp
- `likes`, `retweets`, `replies`: Engagement metrics
- `mentions`, `hashtags`: Extracted entities
- `url`: Tweet URL

### User Model

- `username`: Twitter username
- `display_name`: Profile display name
- `bio`: User biography
- `followers_count`, `following_count`: Follow metrics
- `verified`: Verification status

## 🔧 Development

### Running Tests

```bash
python -m pytest tests/
```

### Code Style

```bash
# Format code
black src/

# Check linting
flake8 src/
```

## 📝 Logging

Logs are configured via `config/logging.yaml` and stored in the `logs/` directory:

- `info.log`: General application logs
- `error.log`: Error-specific logs

## ⚠️ Important Notes

- **Rate Limiting**: Built-in delays help avoid being blocked
- **Ethical Use**: Respect platform terms of service and rate limits
- **Legal Compliance**: Ensure compliance with local laws and platform policies
- **Data Privacy**: Handle scraped data responsibly

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🚨 Disclaimer

This tool is for educational and research purposes only. Users are responsible for ensuring compliance with applicable laws, terms of service, and ethical guidelines when scraping data from social media platforms.

## 🔮 Future Enhancements

- [ ] Support for additional social media platforms
- [ ] API-based scraping methods
- [ ] Real-time data streaming
- [ ] Advanced analytics and visualization
- [ ] Database integration
- [ ] Web interface for configuration and monitoring
