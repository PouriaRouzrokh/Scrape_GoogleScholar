import base64
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List
from pydantic import BaseModel

from src.config import DEFAULT_EXTRACT_MODEL
from src.prompts.digest_first_page_prompt import EXTRACT_FROM_FIRST_PAGE_PROMPT

# Load environment variables
load_dotenv()

class Metrics(BaseModel):
    citations: int
    h_index: int
    i10_index: int
    cited_by_5_years: int

class NewArticle(BaseModel):
    title: str
    url: str

class HomePageExtractionResponse(BaseModel):
    success: bool
    metrics: Metrics
    newest_articles: list[NewArticle]

def encode_image(image_path: str) -> str:
    """
    Encode an image file to base64.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

async def extract_metrics_and_articles(first_page_content: str, screenshot_path: str) -> tuple[bool, dict]:
    """
    Extract the metrics and articles from the Google Scholar home page.

    Args:
        homepage_content (str): The content of the Google Scholar home page.
        screenshot_path (str): The path to the screenshot of the Google Scholar home page.

    Returns:
        bool: True if the metrics and articles are successfully extracted, False otherwise.
        dict: The metrics and articles extracted from the Google Scholar home page.
    """
    client = OpenAI()

    try:
        response = client.responses.parse(
            model=DEFAULT_EXTRACT_MODEL,
            input=[
                {
                    "role": "developer",
                    "content": EXTRACT_FROM_FIRST_PAGE_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"Here is the content of the Google Scholar home page: {first_page_content}"
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{encode_image(screenshot_path)}",
                        }
                    ]
                }
            ],
            text_format=HomePageExtractionResponse
        )
        output = response.output_parsed
        if output.success:
            output = {
                "metrics": {
                    "citations": output.metrics.citations,
                    "h_index": output.metrics.h_index,
                    "i10_index": output.metrics.i10_index,
                    "cited_by_5_years": output.metrics.cited_by_5_years
                },
                "newest_articles": [
                    {"title": article.title, "url": article.url} for article in output.newest_articles
                ]
            }
            return True, output
        else:
            return False, {
                "metrics": {},
                "newest_articles": []
            }
    except Exception as e:
        print(e)
        return False, {
            "metrics": {},
            "newest_articles": []
        }