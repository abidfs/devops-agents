import os
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from state import DevOpsState
from tools import read_log_tool, search_tool

llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    temperature=0.1,
    max_tokens=2048,
    timeout=30,
    max_retries=2,
)

SYSTEM_PROMPT = """You are an expert DevOps engineer. Always provide detailed technical analysis, step-by-step solutions, and production-ready recommendations."""

def log_analyzer_node(state):
    # Direct invocation of the ReadFileTool
    # It will look for the file relative to the root_dir defined in tools.py
    print("Reading log file")
    logs = read_log_tool.invoke({"file_path": state['log_file_path']})
    prompt = f"""
    **Role:** Senior DevOps Troubleshooter with 10 years of experience.
    **Task:** Analyze the production logs provided below to identify critical issues and the root cause of the failure.
    
    **Instructions:**
    1. Review the logs thoroughly.
    2. Extract specific error messages and failure patterns.
    3. Summarize the primary issue clearly.
    
    **Logs:**
    {logs}
    """
    print("Analyzing logs with LLM")
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
    print("Log analyzed with LLM")
    return {"log_analysis": response.content}

def investigator_node(state: DevOpsState):
    print("Searching for solutions based on log analysis online")
    query = f"Solutions for DevOps issue: {state['log_analysis']}"
    search_results = search_tool.invoke(input=query[:400]) # Tavily search tool only supports upto 400 characters.
    prompt = f"""
    **Role:** DevOps Troubleshooting Specialist
    **Task:** Synthesize log evidence with technical research to identify the most viable solution.
    
    **Context:**
    1. LOG ANALYSIS: 
    {state['log_analysis']}

    2. SEARCH RESULTS: 
    {search_results}
    
    **Instructions:**
    - Compare the error patterns in the logs with the search results provided.
    - Filter out irrelevant search results that don't match our specific environment context.
    - Summarize the most reliable remediation steps found, citing official documentation where possible.
    - Identify any common pitfalls or "gotchas" associated with these solutions.
    - Provide a comprehensive investigation report that can be used later to build a final remediation plan.
    """
    print("Summarizing investigation results with LLM")
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
    print("Investigation results summarized with LLM")
    return {"investigation_results": response.content}

def solution_specialist_node(state: DevOpsState):
    prompt = f"""
    **Role:** Senior DevOps Solutions Architect
    **Task:** Generate a production-ready remediation plan based on technical investigation findings.

    **Context:**
    1. INVESTIGATION SUMMARY: 
    {state['investigation_results']}

    2. ROOT CAUSE CONTEXT: 
    {state['log_analysis']}

    **Instructions:**
    - Create a logical, step-by-step remediation plan to resolve the issue.
    - Provide exact shell commands, YAML configurations, or CLI snippets where applicable.
    - Include a "Verification" section to confirm the fix actually works.
    - Add a "Prevention" section with monitoring or configuration best practices to avoid recurrence.
    - Cite official documentation links as references.

    Output format: Use clear Markdown headers, code blocks for commands, and a professional technical tone.
    """
    print("Generating remediation plan with LLM")
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
    print("Remediation plan generated with LLM")
    return {"remediation_plan": response.content}