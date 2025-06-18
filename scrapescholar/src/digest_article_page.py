from litellm import OpenAI
from pydantic import BaseModel

from src.config import DEFAULT_EXTRACT_MODEL
from src.prompts.digest_article_page_prompt import EXTRACT_ARTICLE_DATA_PROMPT

class Article(BaseModel):
    success: bool
    title: str
    authors: str
    year: int
    journal: str
    volume: str
    number: str
    pages: str
    publisher: str
    abstract: str
    num_citations: int
    url: str
    article_id: str
    bibtex: str

async def extract_article_data(article_content: str) -> tuple[bool, dict]:
    """
    Extract the data from the article page.

    Args:
        article_content (str): The content of the article page.

    Returns:
        tuple[bool, dict]: A tuple containing a boolean indicating success and a dictionary of article data.
    """
    client = OpenAI()
    try:
        result = client.responses.parse(
            model=DEFAULT_EXTRACT_MODEL,
            input=[
                {
                    "role": "developer",
                    "content": EXTRACT_ARTICLE_DATA_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"Here is the content of the article page: {article_content}"
                        }
                    ]
                }
            ],
            text_format=Article,
        )
        output = result.output_parsed
        if output.success:
            output = output.model_dump()
            del output["success"]
            return True, output
        else:
            return False, {}
    except Exception as e:
        print(f"Error extracting article data: {e}")
        return False, {}