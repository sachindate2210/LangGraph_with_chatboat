from langchain_core.tools import Tool


def search(query: str) -> str:

    try:

        from ddgs import DDGS

        results = DDGS().text(query, max_results=5)

        if not results:
            return "No search results found."

        return "\n".join([r.get("body", "") for r in results])

    except Exception as e:

        return f"Search Error: {str(e)}"


search_tool = Tool(
    name="Search",
    func=search,
    description="Search the internet for current information"
)