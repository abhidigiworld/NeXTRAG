
from duckduckgo_search import DDGS
import json

def test_search():
    print("Testing DuckDuckGo Search (HTML backend)...")
    try:
        with DDGS() as ddgs:
            # Try using backend='html' if supported, or just catch the error
            print("Attempting search...")
            results = list(ddgs.text("What is the capital of France?", max_results=5, backend="html"))
            
        print(f"Found {len(results)} results:")
        for r in results:
            print(f"- {r['title']}: {r['href']}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search()
