from typing import TypedDict, List, Annotated
import operator

class DevOpsState(TypedDict):
    log_file_path: str
    log_analysis: str
    investigation_results: str
    remediation_plan: str
    # Tracks the history of messages for memory-like behavior
    messages: Annotated[List[str], operator.add]
