from langgraph.graph import StateGraph, END
from state import DevOpsState
from nodes import log_analyzer_node, investigator_node, solution_specialist_node

def create_devops_graph():
    workflow = StateGraph(DevOpsState)

    # Add Nodes
    workflow.add_node("analyze_logs", log_analyzer_node)
    workflow.add_node("investigate_issue", investigator_node)
    workflow.add_node("provide_solution", solution_specialist_node)

    # Define Edges
    workflow.set_entry_point("analyze_logs")
    workflow.add_edge("analyze_logs", "investigate_issue")
    workflow.add_edge("investigate_issue", "provide_solution")
    workflow.add_edge("provide_solution", END)

    return workflow.compile()
