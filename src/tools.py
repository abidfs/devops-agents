import os
from langchain_community.tools.file_management import ReadFileTool
from langchain_tavily import TavilySearch

# Initialize ReadFileTool directly
# root_dir is important for security and resolving relative paths
print(os.getcwd())
read_log_tool = ReadFileTool(root_dir=str(os.getcwd()))

# Initialize Search Tool
search_tool = TavilySearch(
    tavily_api_key=os.getenv("TAVILY_API_KEY"),
    max_results=3
)