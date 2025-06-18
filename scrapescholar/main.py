import asyncio
from datetime import datetime
import json
import os
from src.tools.scrape import (
    create_scholar_crawler, 
    fetch_url_content_with_crawler, 
    cleanup_scholar_session
)
from src.digest_first_page import extract_metrics_and_articles
from src.digest_all_pages import extract_citations_from_all_pages
from src.handle_new_articles import extract_new_articles
from src.update_research_data import create_research_json
from src.config import GOOGLE_SCHOLAR_URL, DATA_DIR

async def run_scraping_process():
    """
    Run the complete Google Scholar scraping process with persistent browser session.
    """
    # ------------------------------------------------------------
    # Step 0: Create the main data directory if it doesn't exist
    # ------------------------------------------------------------
    subdirectory = datetime.now().strftime("%Y-%m-%d")
    main_data_dir = f"{DATA_DIR}/{subdirectory}"
    os.makedirs(main_data_dir, exist_ok=True)
    
    # Create directory structure
    os.makedirs(f"{main_data_dir}/content", exist_ok=True)
    os.makedirs(f"{main_data_dir}/screenshots", exist_ok=True)
    
    print("🚀 Starting Google Scholar scraping process...")
    print(f"📁 Data will be saved to: {main_data_dir}")
    
    # ------------------------------------------------------------
    # Create persistent browser session
    # ------------------------------------------------------------
    print("\n" + "=" * 60)
    print("INITIALIZING BROWSER SESSION")
    print("=" * 60)
    
    crawler = await create_scholar_crawler()
    
    try:
        # ------------------------------------------------------------
        # Step 1: Fetch and save the Google Scholar first page content + screenshot
        # ------------------------------------------------------------
        print("\n" + "=" * 60)
        print("STEP 1: Fetching Google Scholar first page content and screenshot")
        print("=" * 60)
        
        first_page_content_path = f"{main_data_dir}/content/first_page_content.md"
        first_page_screenshot_path = f"{main_data_dir}/screenshots/first_page_screenshot.png"
        
        success, first_page_content, screenshot_success = await fetch_url_content_with_crawler(
            crawler, GOOGLE_SCHOLAR_URL, first_page_screenshot_path, 
            wait_for_user=True, is_first_load=True
        )
        
        if success:
            with open(first_page_content_path, "w", encoding="utf-8") as f:
                f.write(first_page_content)
            print("✅ Successfully fetched the first page of the Google Scholar author profile.")
            
            if screenshot_success:
                print("✅ Successfully took screenshot of the Google Scholar home page.")
            else:
                print("⚠️  Screenshot failed but content was extracted successfully.")
        else:
            print("❌ Failed to fetch the first page of the Google Scholar author profile.")
            print("Exiting...")
            return

        # ------------------------------------------------------------
        # Step 2: Fetch and save the Google Scholar full page content
        # ------------------------------------------------------------
        print("\n" + "=" * 60)
        print("STEP 2: Fetching Google Scholar full page content")
        print("=" * 60)
        
        full_page_url = f"{GOOGLE_SCHOLAR_URL}&pagesize=100"
        full_page_content_path = f"{main_data_dir}/content/full_page_content.md"
        
        success, full_page_content, _ = await fetch_url_content_with_crawler(
            crawler, full_page_url, wait_for_user=False, is_first_load=False
        )
        
        if success:
            with open(full_page_content_path, "w", encoding="utf-8") as f:
                f.write(full_page_content)
            print("✅ Successfully fetched the full page of the Google Scholar author profile.")
        else:
            print("❌ Failed to fetch the full page of the Google Scholar author profile.")

        # ------------------------------------------------------------
        # Step 3: Extract the metrics and articles from the Google Scholar first page and save it
        # ------------------------------------------------------------
        print("\n" + "=" * 60)
        print("STEP 3: Extracting metrics and articles from first page")
        print("=" * 60)
        
        success, metrics_and_articles = await extract_metrics_and_articles(first_page_content, first_page_screenshot_path)
        if success:
            print("✅ Successfully extracted the metrics and articles from the Google Scholar first page.")
            with open(f"{main_data_dir}/metrics_and_articles.json", "w", encoding="utf-8") as f:
                json.dump(metrics_and_articles, f, indent=2)
        else:
            print("❌ Failed to extract the metrics and articles from the Google Scholar home page.")

        # ------------------------------------------------------------
        # Step 4: Extract the articles and citations from the Google Scholar full page and save it
        # ------------------------------------------------------------
        print("\n" + "=" * 60)
        print("STEP 4: Extracting citations from full page")
        print("=" * 60)
        
        success, article_citations = await extract_citations_from_all_pages(full_page_content)
        if success:
            with open(f"{main_data_dir}/article_citations.json", "w", encoding="utf-8") as f:
                json.dump(article_citations, f, indent=2)
            print("✅ Successfully extracted the articles and citations from the Google Scholar full page.")
        else:
            print("❌ Failed to extract the articles and citations from the Google Scholar full page.")

        # ------------------------------------------------------------
        # Step 5: Extract the data from new articles, if any. 
        # ------------------------------------------------------------
        print("\n" + "=" * 60)
        print("STEP 5: Processing new articles")
        print("=" * 60)
        
        success, num_success = await extract_new_articles(metrics_and_articles, main_data_dir, crawler)
        if success:
            print(f"✅ Successfully extracted the data from {num_success} new articles.")
        else:
            print("❌ Failed to extract the data from new articles.")

        # ------------------------------------------------------------
        # Step 6: Create a new research json file
        # ------------------------------------------------------------
        print("\n" + "=" * 60)
        print("STEP 6: Creating research JSON file")
        print("=" * 60)
        
        success = create_research_json(main_data_dir)
        if success:
            print("✅ Successfully created the research json file.")
            print(f"📁 All data saved to: {main_data_dir}")
        else:
            print("❌ Failed to create the research json file.")
    
    finally:
        # Always clean up the browser session
        print("\n" + "=" * 60)
        print("CLEANING UP")
        print("=" * 60)
        
        await cleanup_scholar_session(crawler)
        await crawler.__aexit__(None, None, None)  # Close the crawler properly
        print("✅ Browser session closed successfully")

def main():
    """Main entry point - runs the async scraping process."""
    asyncio.run(run_scraping_process())

if __name__ == "__main__":
    main()
