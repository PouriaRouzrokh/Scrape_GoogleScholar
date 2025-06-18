import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
import os
from base64 import b64decode

# Global session configuration
SCHOLAR_SESSION_ID = "persistent_scholar_session"

async def create_scholar_crawler(width: int = 1920, height: int = 2280) -> AsyncWebCrawler:
    """
    Create a crawler configured for Google Scholar with interactive captcha handling.
    
    Args:
        width (int): Viewport width in pixels (default: 1920)
        height (int): Viewport height in pixels (default: 2280)
    
    Returns:
        AsyncWebCrawler: Configured crawler instance
    """
    browser_config = BrowserConfig(
        headless=False,  # Visible browser for captcha handling
        verbose=True,
        viewport_width=width,
        viewport_height=height,
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.__aenter__()  # Initialize the crawler
    return crawler

async def fetch_url_content_with_crawler(crawler: AsyncWebCrawler, url: str, screenshot_path: str = None, 
                                       wait_for_user: bool = False, is_first_load: bool = False) -> tuple[bool, str, bool]:
    """
    Fetch URL content using an existing crawler session.
    
    Args:
        crawler: Existing AsyncWebCrawler instance
        url: URL to fetch
        screenshot_path: Optional path to save screenshot
        wait_for_user: Whether to wait for user confirmation before proceeding
        is_first_load: Whether this is the first load in the session
    
    Returns:
        tuple: (content_success: bool, markdown_content: str, screenshot_success: bool)
    """
    try:
        # Ensure screenshot directory exists if path provided
        if screenshot_path:
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        
        if is_first_load:
            print(f"\n🌐 Opening {url} in browser...")
            print("📝 Please handle any captcha or verification if needed.")
            print("✅ When the page is fully loaded and ready, press ENTER to continue...")
            
            # First load in session
            config = CrawlerRunConfig(
                session_id=SCHOLAR_SESSION_ID,
                wait_for="css:body",
                cache_mode=CacheMode.BYPASS
            )
            
            result = await crawler.arun(url=url, config=config)
            
            if not result.success:
                return False, f"Failed to load page: {result.error_message}", False
            
            if wait_for_user:
                # Wait for user confirmation that captcha is handled
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, input)
            
            print("📄 Extracting page content...")
            
            # Re-run to get fresh content after user interaction
            final_config = CrawlerRunConfig(
                session_id=SCHOLAR_SESSION_ID,
                js_only=True,
                cache_mode=CacheMode.BYPASS,
                screenshot=screenshot_path is not None,
                screenshot_wait_for=1.0
            )
            
            final_result = await crawler.arun(url=url, config=final_config)
            
        else:
            # Subsequent loads in same session - just navigate to the new URL
            print(f"🔄 Navigating to {url} in existing session...")
            
            # Wait a moment for any previous navigation to complete
            await asyncio.sleep(1)
            
            config = CrawlerRunConfig(
                session_id=SCHOLAR_SESSION_ID,
                js_only=True,
                cache_mode=CacheMode.BYPASS,
                screenshot=screenshot_path is not None,
                screenshot_wait_for=1.0 if screenshot_path else None,
                # Use JavaScript to navigate to new URL in same session
                js_code=f"window.location.href = '{url}'; await new Promise(resolve => setTimeout(resolve, 3000));"
            )
            
            final_result = await crawler.arun(url=url, config=config)
        
        if not final_result.success:
            return False, f"Failed to extract content: {final_result.error_message}", False
        
        # Handle screenshot if requested
        screenshot_success = True
        if screenshot_path and final_result.screenshot:
            try:
                print("📸 Saving screenshot...")
                with open(screenshot_path, "wb") as f:
                    f.write(b64decode(final_result.screenshot))
                print(f"✅ Screenshot saved to: {screenshot_path}")
            except Exception as e:
                print(f"❌ Error saving screenshot: {e}")
                screenshot_success = False
        elif screenshot_path and not final_result.screenshot:
            print("⚠️  Screenshot was requested but not captured by crawl4ai")
            screenshot_success = False
        
        return True, final_result.markdown, screenshot_success
        
    except Exception as e:
        print(f"❌ Error in browser operation: {e}")
        return False, f"Failed to fetch content: {e}", False

async def cleanup_scholar_session(crawler: AsyncWebCrawler):
    """Clean up the persistent scholar session."""
    try:
        # Try to kill the session (though newer versions auto-manage this)
        if hasattr(crawler, 'crawler_strategy') and hasattr(crawler.crawler_strategy, 'kill_session'):
            await crawler.crawler_strategy.kill_session(SCHOLAR_SESSION_ID)
            print("🧹 Cleaned up browser session")
        else:
            print("🧹 Session cleanup handled automatically by crawl4ai")
    except Exception as e:
        print(f"🧹 Session cleanup handled automatically (crawl4ai v0.6.3+): {e}")