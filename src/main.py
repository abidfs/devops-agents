import os
from dotenv import load_dotenv
# Load .env
load_dotenv()

from graph import create_devops_graph

app = create_devops_graph()

def run_analysis(log_path):
    # Ensure output directory exists
    os.makedirs("task_outputs", exist_ok=True)
    
    initial_state = {
        "log_file_path": log_path,
        "messages": []
    }
    
    print(f"🚀 Starting DevOps Analysis for {log_path}...")
    final_state = app.invoke(initial_state)
    
    print("\n--- FINAL SOLUTION ---")
    print(final_state["remediation_plan"])
    
    # Optional: Save to file for review
    with open("task_outputs/remediation_plan.md", "w") as f:
        f.write(final_state["remediation_plan"])

if __name__ == "__main__":
    run_analysis("./sample_error_logs/sample1.log")