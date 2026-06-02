import webbrowser
from utils.logger import get_logger

logger = get_logger(__name__)

def search_google(query: str) -> str:
    """Opens Google search with the specified query."""
    try:
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return f"Searching Google for '{query}'..."
    except Exception as e:
        logger.error(f"Failed to perform search: {e}")
        return "Sorry, I encountered an error while searching."
