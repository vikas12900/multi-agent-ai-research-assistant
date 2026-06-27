from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()

client = TavilyClient(api_key = os.getenv("TAVILY_API_KEY"))

def researcher_agent(query:str):
    response = client.search(
        query = query,
        search_depth = "advanced",
        max_results = 5
    )

    content = "\n\n".join(
        f"Source: {result['url']}\n{result['content']}"
        for result in response["results"]
    )
    return content