
from duckduckgo_search import DDGS
import json

def test_search():
    print("Testing DuckDuckGo Search...")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text("What is the capital of France?", max_results=5))
            
        print(f"Found {len(results)} results:")
        for r in results:
            print(f"- {r['title']}: {r['href']}")
            print(f"  Snippet: {r['body'][:100]}...")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search()
