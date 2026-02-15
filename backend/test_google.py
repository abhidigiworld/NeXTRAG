
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

try:
    print("Testing models/text-embedding-004...")
    result = genai.embed_content(
        model="models/text-embedding-004",
        content="Hello world",
        task_type="retrieval_document"
    )
    print("Success! Dimension:", len(result['embedding']))
except Exception as e:
    print(f"Failed: {e}")

try:
    print("Testing models/embedding-001...")
    result = genai.embed_content(
        model="models/embedding-001",
        content="Hello world",
        task_type="retrieval_document"
    )
    print("Success! Dimension:", len(result['embedding']))
except Exception as e:
    print(f"Failed: {e}")
