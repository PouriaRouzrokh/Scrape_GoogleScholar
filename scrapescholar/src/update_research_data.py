from datetime import datetime
import json
import os

from src.config import DATA_DIR

def create_research_json(main_data_dir: str) -> bool:
    """
    Create a new research json file.
    """
    
    # Load the most recent research json file
    research_json_folder_path = os.path.join(DATA_DIR, "research_json_archive")
    current_research_json_paths = [f for f in os.listdir(research_json_folder_path) if f.endswith(".json")]
    most_recent_research_json_path = max(current_research_json_paths, key=lambda x: datetime.strptime(x, "%Y-%m-%d.json"))
    with open(os.path.join(research_json_folder_path, most_recent_research_json_path), "r") as f:
        previous_research_json = json.load(f)
    new_research_json = previous_research_json.copy()

    # Load the new articles
    new_articles_dir = os.path.join(main_data_dir, "content", "new_articles")
    new_article_paths = [f for f in os.listdir(new_articles_dir) if f.endswith(".json")]
    new_article_paths.sort(key=lambda x: int(x.split(".")[0]))
    new_articles = [json.load(open(os.path.join(new_articles_dir, new_article_path), "r")) for new_article_path in new_article_paths]

    # Update the research json file with the new articles
    new_research_json["articles"] = new_articles + previous_research_json["articles"]

    # Update the total articles and individual article citations
    article_citations = json.load(open(os.path.join(main_data_dir, "article_citations.json"), "r"))
    for article in new_research_json["articles"]:
        if article["title"] in article_citations:
            article["num_citations"] = article_citations[article["title"]]
        else:
            print(f"warning: article {article['title']} not found in article_citations.json")

    # Update the metadata
    updated_metrics = json.load(open(os.path.join(main_data_dir, "metrics_and_articles.json"), "r"))["metrics"]
    new_research_json["total_articles"] = len(article_citations)
    new_research_json["total_articles_processed"] = len(new_research_json["articles"])
    new_research_json["metrics"]["citations"] = updated_metrics["citations"]
    new_research_json["total_citations"] = updated_metrics["citations"]
    new_research_json["total_citations_processed"] = sum([article["num_citations"] for article in new_research_json["articles"]])
    new_research_json["metrics"]["h_index"] = updated_metrics["h_index"]
    new_research_json["metrics"]["i10_index"] = updated_metrics["i10_index"]
    new_research_json["metrics"]["cited_by_5_years"] = updated_metrics["cited_by_5_years"]
    
    # Save the new research json file
    with open(os.path.join(research_json_folder_path, f"{datetime.now().strftime('%Y-%m-%d')}.json"), "w") as f:
        json.dump(new_research_json, f)

    return True