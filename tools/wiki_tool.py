from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import Tool


def wiki_search(query: str) -> str:

    try:

        wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

        return wiki.run(query)

    except Exception as e:

        return f"Wikipedia unavailable: {str(e)}"


wiki_tool = Tool(
    name="Wikipedia",
    func=wiki_search,
    description="Search Wikipedia for factual information about people, places, and events"
)