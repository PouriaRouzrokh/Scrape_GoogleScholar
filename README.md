# 🎓 Google Scholar Profile Scraper

An automated tool for scraping and monitoring Google Scholar author profiles with AI-powered content extraction and analysis. This tool provides intelligent captcha handling, persistent browser sessions, and structured data extraction for research tracking and analysis.

## 🚀 Features

### 📊 **Comprehensive Data Extraction**

- **Author Metrics**: Citations, h-index, i10-index, 5-year citation counts
- **Publication Lists**: Complete publication history with metadata
- **Citation Tracking**: Individual paper citation counts and trends
- **New Publication Detection**: Automatically identifies newly published papers

### 🤖 **AI-Powered Processing**

- **Structured Data Extraction**: Uses OpenAI GPT models to parse and structure content
- **Smart Content Analysis**: Extracts titles, authors, journals, abstracts, and bibliographic data
- **Automated Classification**: Organizes publications by type and relevance

### 🌐 **Intelligent Web Scraping**

- **Single Session Management**: Handles captcha once, reuses browser session for all operations
- **Visual Browser Interaction**: Opens visible browser for manual captcha solving
- **Robust Content Extraction**: Uses crawl4ai for reliable markdown conversion
- **Screenshot Capture**: Takes screenshots for visual verification and AI analysis

### 📁 **Organized Data Storage**

- **Daily Snapshots**: Creates timestamped directories for each scraping session
- **Multiple Formats**: Saves content as markdown, JSON, and screenshots
- **Historical Tracking**: Maintains archive of research data over time
- **Structured Output**: Organized file hierarchy for easy analysis

## 🛠 Installation

### Prerequisites

- Python 3.12+
- OpenAI API key (for AI-powered extraction)
- Internet connection

### Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Scrape_GoogleScholar
   ```

2. **Install dependencies using uv**

   ```bash
   uv sync
   ```

3. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Update configuration**
   - Edit `scrapescholar/src/config.py`
   - Set `GOOGLE_SCHOLAR_URL` to your target scholar profile
   - Adjust `DATA_DIR` path as needed

## 🎯 Usage

### Basic Usage

```bash
uv run scrapescholar/main.py
```

### What Happens During Execution

1. **Browser Session Initialization**

   - Opens a visible browser window
   - Navigates to the Google Scholar profile

2. **Captcha Handling**

   - **You handle any captcha/verification manually**
   - Press ENTER when the page is ready
   - **This only happens once** - subsequent operations reuse the session

3. **Automated Data Collection**

   - Scrapes the first page (recent publications + metrics)
   - Fetches full publication list (with `pagesize=100`)
   - Takes screenshots for AI analysis
   - Extracts detailed data from new publications

4. **AI Processing**

   - Processes content with OpenAI models
   - Extracts structured metrics and publication data
   - Generates comprehensive research summaries

5. **Data Storage**
   - Saves all data to timestamped directory
   - Creates multiple output formats
   - Updates historical archive

## 📂 Output Structure

Each run creates a directory under `data/YYYY-MM-DD/` containing:

```
data/2025-06-18/
├── content/
│   ├── first_page_content.md       # Main profile page content
│   ├── full_page_content.md        # Complete publication list
│   └── new_articles/               # Individual new publication data
│       ├── 1.md                    # Article content
│       └── 1.json                  # Extracted article metadata
├── screenshots/
│   └── first_page_screenshot.png   # Visual capture for AI analysis
├── metrics_and_articles.json       # Author metrics + recent publications
├── article_citations.json          # Citation counts per publication
└── research_data.json              # Final consolidated research summary
```

## 🔧 Configuration

### Google Scholar Profile

Edit `scrapescholar/src/config.py`:

```python
# Set your target Google Scholar profile URL
GOOGLE_SCHOLAR_URL = "https://scholar.google.com/citations?hl=en&user=YOUR_USER_ID&view_op=list_works&sortby=pubdate"

# Configure data storage location
DATA_DIR = "/path/to/your/data/directory"

# Set OpenAI model for extraction
DEFAULT_EXTRACT_MODEL = "gpt-4.1"
```

### Environment Variables

Create `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## 🔄 How It Works

### 1. **Session Management**

- Creates a single persistent browser session using crawl4ai
- Handles captcha once at the beginning
- Reuses the same session for all subsequent operations
- Eliminates multiple captcha prompts

### 2. **Content Extraction**

- Uses crawl4ai for robust web scraping
- Converts HTML to clean markdown format
- Captures screenshots for visual AI analysis
- Handles dynamic content loading

### 3. **AI Processing**

- Sends content to OpenAI models for structured extraction
- Uses custom prompts for specific data extraction tasks
- Validates and structures output using Pydantic models
- Handles multiple content types (profiles, articles, citations)

### 4. **Data Management**

- Compares with historical data to identify new publications
- Organizes data in timestamped directories
- Maintains clean separation between raw and processed data
- Provides both human-readable and machine-processable formats

## 🎯 Use Cases

- **Research Monitoring**: Track publication metrics and citation growth
- **Academic Analytics**: Analyze research output and impact trends
- **Profile Management**: Monitor Google Scholar profile changes
- **Data Collection**: Gather structured publication data for analysis
- **Citation Tracking**: Monitor how publications are being cited over time

## 🛡 Best Practices

- **Respect Rate Limits**: The tool includes natural delays and handles sessions responsibly
- **Monitor Usage**: Check Google Scholar's terms of service for acceptable use
- **Data Privacy**: Ensure you have permission to scrape the target profiles
- **Regular Updates**: Run periodically to track changes and new publications

## 🔍 Technical Details

### Dependencies

- **crawl4ai**: Advanced web scraping with browser automation
- **OpenAI**: AI-powered content extraction and structuring
- **Playwright**: Browser automation and interaction
- **Pydantic**: Data validation and serialization

### Architecture

- **Modular Design**: Separate modules for scraping, processing, and storage
- **Async Processing**: Efficient handling of web requests and AI API calls
- **Error Handling**: Robust error recovery and logging
- **Session Persistence**: Smart browser session management

## 📊 Example Output

The tool generates structured data like:

```json
{
  "metrics": {
    "citations": 1250,
    "h_index": 18,
    "i10_index": 25,
    "cited_by_5_years": 890
  },
  "newest_articles": [
    {
      "title": "Advanced Machine Learning Applications in Healthcare",
      "url": "https://scholar.google.com/citations?view_op=view_citation&..."
    }
  ]
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is for educational and research purposes. Please ensure compliance with Google Scholar's terms of service and applicable data protection regulations.

---

**⚠️ Important**: This tool requires manual captcha solving and should be used responsibly in accordance with Google Scholar's terms of service.
