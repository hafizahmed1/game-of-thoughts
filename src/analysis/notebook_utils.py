from __future__ import annotations
import pandas as pd
from pathlib import Path
from IPython.display import display, Markdown
from src.analysis.experiment_utils import (
    find_project_root, 
    load_all_simulation_traces,
    compare_models_summary,
    reconstruct_ttt_boards,
    reconstruct_cf_boards
)

def safe_read_csv(path: Path) -> pd.DataFrame:
    """Helper to read CSVs without crashing if they are missing."""
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)

def show_all_experiment_summaries():
    """Displays all key results tables with headers."""
    root = find_project_root()
    tables_dir = root / "results" / "tables"
    
    display(Markdown("# 📊 Global Experiment Results"))
    
    # Map of internal filename to display title
    config = {
        "rule_understanding_results.csv": "🔍 Rule Understanding (Completeness)",
        "rule_error_results.csv": "🚫 Rule Error Detection (F1 Score)",
        "generation_results.csv": "🎨 Game Generation (Clarity & Fun)",
    }
    
    for filename, title in config.items():
        df = safe_read_csv(tables_dir / filename)
        display(Markdown(f"### {title}"))
        if not df.empty:
            display(df)
        else:
            print(f"No data found for {filename}.")

def show_trace_evolution(case_id: str):
    """Visualizes the board-by-board history of a specific case."""
    traces = load_all_simulation_traces()
    case = next((c for c in traces if c.get("case_id") == case_id), None)
    
    if not case:
        print(f"Case {case_id} not found.")
        return

    game = case.get("game")
    states = reconstruct_ttt_boards(case) if game == "tictactoe" else reconstruct_cf_boards(case)
    
    display(Markdown(f"## 🎮 Case Deep Dive: `{case_id}`"))
    display(Markdown(f"**Model:** {case.get('model')} | **Result:** {case.get('winner')}"))
    
    for label, board in states:
        display(Markdown(f"**{label}**"))
        # Print board inside a code block for fixed-width alignment
        print(board)
        print("-" * 20)

def show_simulation_performance():
    """Shows the detailed win/accuracy rates for simulations."""
    traces = load_all_simulation_traces()
    if not traces:
        print("No simulation traces found.")
        return
        
    summary_df = compare_models_summary(traces)
    display(Markdown("## 🤖 Simulation Performance Summary"))
    display(summary_df)