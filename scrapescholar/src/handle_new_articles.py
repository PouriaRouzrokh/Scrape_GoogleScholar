import asyncio
import os
import re
from src.config import DEFAULT_EXTRACT_MODEL, DATA_DIR
from src.tools.scrape import fetch_url_content_with_crawler
from src.digest_article_page import extract_article_data
import json
from datetime import datetime
from pydantic import BaseModel

def clean_title(title: str) -> str:
    """
    Clean and normalize article titles.
    
    Args:
        title (str): Raw title string
        
    Returns:
        str: Cleaned title
    """
    title = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', title)
    title = re.sub(r'\s+', ' ', title).strip()
    title = title.strip('|[](){}')
    title = title.replace('\\(', '(').replace('\\)', ')')
    
    return title

async def extract_new_articles(metrics_and_articles: dict, main_data_dir: str, crawler=None) -> tuple[bool, int]:
    """
    Extract the data from new articles, if any.
    
    Args:
        metrics_and_articles: Dictionary containing metrics and newest articles
        main_data_dir: Directory to save extracted data
        crawler: Optional AsyncWebCrawler instance to reuse existing session
    
    Returns:
        tuple: (success: bool, num_success: int)
    """

    # Load the previous article list
    research_json_folder_path = os.path.join(DATA_DIR, "research_json_archive")
    
    # Check if research_json_archive directory exists
    if not os.path.exists(research_json_folder_path):
        print("⚠️  No previous research data found - treating all articles as new")
        previous_article_titles = []
    else:
        current_research_json_paths = [f for f in os.listdir(research_json_folder_path) if f.endswith(".json")]
        
        if not current_research_json_paths:
            print("⚠️  No previous research JSON files found - treating all articles as new")
            previous_article_titles = []
        else:
            most_recent_research_json_path = max(current_research_json_paths, key=lambda x: datetime.strptime(x, "%Y-%m-%d.json"))
            with open(os.path.join(research_json_folder_path, most_recent_research_json_path), "r") as f:
                previous_research_json = json.load(f)
            previous_articles = previous_research_json["articles"]
            previous_article_titles = [clean_title(article["title"]) for article in previous_articles]
    
    # Find the new articles
    newest_articles = metrics_and_articles.get("newest_articles", [])
    new_articles = [article for article in newest_articles if clean_title(article["title"]) not in previous_article_titles]
    
    if not new_articles:
        print("✅ No new articles found to process")
        return True, 0

    print(f"📝 Found {len(new_articles)} new articles to process")

    # Fetch the markdown content of the new articles and digest them
    new_articles_dir = os.path.join(main_data_dir, "content", "new_articles")
    os.makedirs(new_articles_dir, exist_ok=True)
    num_success = 0
    
    for i, article in enumerate(new_articles):
        article_url = article["url"]
        article_title = article["title"]
        
        print(f"🔄 Processing article {i+1}/{len(new_articles)}: {article_title[:50]}...")
        
        if crawler:
            # Use existing crawler session
            success, article_content, _ = await fetch_url_content_with_crawler(
                crawler, article_url, wait_for_user=False, is_first_load=False
            )
        else:
            # Fallback: create temporary crawler (not recommended for multiple articles)
            print("⚠️  No crawler provided - creating temporary session (may require additional captcha)")
            from src.tools.scrape import create_scholar_crawler, cleanup_scholar_session
            temp_crawler = await create_scholar_crawler()
            try:
                success, article_content, _ = await fetch_url_content_with_crawler(
                    temp_crawler, article_url, wait_for_user=True, is_first_load=True
                )
                await cleanup_scholar_session(temp_crawler)
            finally:
                await temp_crawler.__aexit__(None, None, None)
            success = success  # Keep the same variable name for consistency
        
        if success:
            # Save the markdown content
            with open(os.path.join(new_articles_dir, f"{i+1}.md"), "w", encoding="utf-8") as f:
                f.write(article_content)
            
            # Extract article data
            success, article_data = await extract_article_data(article_content)
            if success:
                with open(os.path.join(new_articles_dir, f"{i+1}.json"), "w", encoding="utf-8") as f:
                    json.dump(article_data, f, indent=2)
                print(f"✅ Successfully extracted data for: {article_title}")
                num_success += 1
            else:
                print(f"❌ Failed to extract data for: {article_title}")
        else:
            print(f"❌ Failed to fetch content for: {article_title}")
            continue
    
    return True, num_success