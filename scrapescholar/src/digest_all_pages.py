from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List
from pydantic import BaseModel

from src.config import DEFAULT_EXTRACT_MODEL
from src.prompts.digest_all_pages_prompt import EXTRACT_FROM_ALL_PAGES_PROMPT

# Load environment variables
load_dotenv()

class ArticleCitations(BaseModel):
    title: str
    citations: int

class ArticleCitationsResponse(BaseModel):
    success: bool
    article_citations: list[ArticleCitations]

async def extract_citations_from_all_pages(full_page_content: str) -> tuple[bool, dict]:
    """
    Extract the articles and citations from the Google Scholar full page.

    Args:
        full_page_content (str): The content of the Google Scholar full page.

    Returns:
        tuple[bool, dict]: A tuple containing a boolean indicating success and a dictionary of article citations.
    """
    client = OpenAI()
    try:
        result = client.responses.parse(
            model=DEFAULT_EXTRACT_MODEL,
            input=[
                {
                    "role": "developer",
                    "content": EXTRACT_FROM_ALL_PAGES_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"Here is the content of the Google Scholar full page: {full_page_content}"
                        }
                    ]
                }
            ],
            text_format=ArticleCitationsResponse,
        )
        output = result.output_parsed
        if output.success:
            output = {
                article.title: article.citations for article in output.article_citations
            }
            return True, output
        else:
            return False, {}
    except Exception as e:
        print(e)
        return False, {}
