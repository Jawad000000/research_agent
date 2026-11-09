# main.py
from src.tools.tools import web_search

result = web_search.invoke({"query": "latest research on AI in healthcare"})
print(result)
