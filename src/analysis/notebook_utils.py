from __future__ import annotations

from IPython.display import Markdown, display

from src.analysis.experiment_utils import (
    find_project_root,
    safe_read_csv,
    load_all_simulation_traces,
    compare_models_summary,
    reconstruct_ttt_boards,
    reconstruct_cf_boards,
)


def show_all_experiment_summaries():
    root = find_project_root()
    tables_dir = root / "results" / "tables"

    display(Markdown("# Global Experiment Results"))

    config = {
        "rule_understanding_results.csv": "Rule Understanding",
        "rule_error_results.csv": "Rule Error Detection",
        "generation_results.csv": "Game Generation",
    }

    for filename, title in config.items():
        df = safe_read_csv(tables_dir / filename)
        display(Markdown(f"### {title}"))
        if not df.empty:
            display(df)
        else:
            print(f"No data found for {filename}.")


def show_trace_evolution(case_id: str):
    traces = load_all_simulation_traces()
    case = next((c for c in traces if c.get("case_id") == case_id), None)

    if not case:
        print(f"Case {case_id} not found.")
        return

    game = case.get("game")

    if game == "tictactoe":
        states = reconstruct_ttt_boards(case)
    elif game == "connect_four":
        states = reconstruct_cf_boards(case)
    else:
        print(f"Unsupported game: {game}")
        return

    display(Markdown(
        f"## Case Deep Dive: `{case_id}`\n"
        f"**Model:** `{case.get('model', 'unknown')}`  \n"
        f"**Game:** `{case.get('game', 'unknown')}`  \n"
        f"**Stopped reason:** `{case.get('stopped_reason', 'unknown')}`  \n"
        f"**Winner:** `{case.get('winner', 'unknown')}`"
    ))

    for label, board in states:
        display(Markdown(f"**{label}**"))
        print(board)
        print("-" * 20)


def show_simulation_performance():
    traces = load_all_simulation_traces()

    if not traces:
        print("No simulation traces found.")
        return

    summary_df = compare_models_summary(traces)
    display(Markdown("## Simulation Performance Summary"))
    display(summary_df)