from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd


def load_simulation_data(input_path: Path) -> pd.DataFrame:
    if input_path.is_file():
        df = pd.read_csv(input_path)
        return df

    csv_files = sorted(
        p for p in input_path.glob("*_simulation_results.csv")
        if p.name != "all_simulation_results.csv"
    )

    if not csv_files:
        raise FileNotFoundError(
            f"No simulation CSV files found in: {input_path}"
        )

    frames = []
    for csv_file in csv_files:
        frames.append(pd.read_csv(csv_file))

    return pd.concat(frames, ignore_index=True)


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Normalize text columns
    for col in ["winner", "stopped_reason", "model", "game", "provider"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)

    # Case-level metrics
    df["is_completed"] = df["stopped_reason"].eq("terminal_state_reached")
    df["is_initially_terminal"] = df["total_turns"].eq(0) & df["completed_turns"].eq(0)
    df["is_non_terminal_case"] = ~df["is_initially_terminal"]
    df["has_invalid_turn"] = df["invalid_turns"] > 0
    df["has_valid_turn"] = df["valid_turns"] > 0

    # Safe division
    df["move_accuracy_case"] = df.apply(
        lambda row: (row["valid_turns"] / row["total_turns"]) if row["total_turns"] > 0 else 0.0,
        axis=1,
    )
    df["invalid_move_rate_case"] = df.apply(
        lambda row: (row["invalid_turns"] / row["total_turns"]) if row["total_turns"] > 0 else 0.0,
        axis=1,
    )

    # Winner helpers
    df["x_win"] = df["winner"].eq("X")
    df["o_win"] = df["winner"].eq("O")
    df["draw"] = df["winner"].str.lower().eq("draw")

    return df


def summarize_all_cases(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby(["model", "game"], dropna=False)

    summary = grouped.agg(
        cases=("case_id", "count"),
        completed_cases=("is_completed", "sum"),
        non_terminal_cases=("is_non_terminal_case", "sum"),
        terminal_start_cases=("is_initially_terminal", "sum"),
        total_turns=("total_turns", "sum"),
        valid_turns=("valid_turns", "sum"),
        invalid_turns=("invalid_turns", "sum"),
        avg_completed_turns=("completed_turns", "mean"),
        x_wins=("x_win", "sum"),
        o_wins=("o_win", "sum"),
        draws=("draw", "sum"),
    ).reset_index()

    summary["completion_rate"] = summary["completed_cases"] / summary["cases"]
    summary["move_accuracy"] = summary.apply(
        lambda row: (row["valid_turns"] / row["total_turns"]) if row["total_turns"] > 0 else 0.0,
        axis=1,
    )
    summary["invalid_move_rate"] = summary.apply(
        lambda row: (row["invalid_turns"] / row["total_turns"]) if row["total_turns"] > 0 else 0.0,
        axis=1,
    )

    # Win rates among completed cases only
    summary["x_win_rate"] = summary.apply(
        lambda row: (row["x_wins"] / row["completed_cases"]) if row["completed_cases"] > 0 else 0.0,
        axis=1,
    )
    summary["o_win_rate"] = summary.apply(
        lambda row: (row["o_wins"] / row["completed_cases"]) if row["completed_cases"] > 0 else 0.0,
        axis=1,
    )
    summary["draw_rate"] = summary.apply(
        lambda row: (row["draws"] / row["completed_cases"]) if row["completed_cases"] > 0 else 0.0,
        axis=1,
    )

    return summary.sort_values(["game", "model"]).reset_index(drop=True)


def summarize_non_terminal_cases_only(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df[df["is_non_terminal_case"]].copy()

    if filtered.empty:
        return pd.DataFrame()

    grouped = filtered.groupby(["model", "game"], dropna=False)

    summary = grouped.agg(
        non_terminal_cases=("case_id", "count"),
        completed_cases=("is_completed", "sum"),
        total_turns=("total_turns", "sum"),
        valid_turns=("valid_turns", "sum"),
        invalid_turns=("invalid_turns", "sum"),
        avg_completed_turns=("completed_turns", "mean"),
        x_wins=("x_win", "sum"),
        o_wins=("o_win", "sum"),
        draws=("draw", "sum"),
    ).reset_index()

    summary["completion_rate"] = summary["completed_cases"] / summary["non_terminal_cases"]
    summary["move_accuracy"] = summary.apply(
        lambda row: (row["valid_turns"] / row["total_turns"]) if row["total_turns"] > 0 else 0.0,
        axis=1,
    )
    summary["invalid_move_rate"] = summary.apply(
        lambda row: (row["invalid_turns"] / row["total_turns"]) if row["total_turns"] > 0 else 0.0,
        axis=1,
    )
    summary["x_win_rate"] = summary.apply(
        lambda row: (row["x_wins"] / row["completed_cases"]) if row["completed_cases"] > 0 else 0.0,
        axis=1,
    )
    summary["o_win_rate"] = summary.apply(
        lambda row: (row["o_wins"] / row["completed_cases"]) if row["completed_cases"] > 0 else 0.0,
        axis=1,
    )
    summary["draw_rate"] = summary.apply(
        lambda row: (row["draws"] / row["completed_cases"]) if row["completed_cases"] > 0 else 0.0,
        axis=1,
    )

    return summary.sort_values(["game", "model"]).reset_index(drop=True)


def percent_columns(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    out = df.copy()
    for col in columns:
        if col in out.columns:
            out[col] = (out[col] * 100).round(2)
    return out


def save_markdown_table(df: pd.DataFrame, output_path: Path, title: str) -> None:
    lines = [f"# {title}", ""]
    lines.append(df.to_markdown(index=False))
    lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def plot_metric_by_game(summary_df: pd.DataFrame, metric: str, ylabel: str, output_path: Path) -> None:
    if summary_df.empty:
        return

    pivot = summary_df.pivot(index="game", columns="model", values=metric).fillna(0)

    ax = pivot.plot(kind="bar", figsize=(9, 5))
    ax.set_title(metric.replace("_", " ").title())
    ax.set_xlabel("Game")
    ax.set_ylabel(ylabel)
    ax.legend(title="Model")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_stacked_outcomes(summary_df: pd.DataFrame, output_path: Path) -> None:
    if summary_df.empty:
        return

    df = summary_df.copy()
    df["label"] = df["game"] + " | " + df["model"]

    plot_df = df.set_index("label")[["x_wins", "o_wins", "draws"]]
    ax = plot_df.plot(kind="bar", stacked=True, figsize=(10, 5))
    ax.set_title("Completed Game Outcomes")
    ax.set_xlabel("Game | Model")
    ax.set_ylabel("Count")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze simulation CSV results.")
    parser.add_argument(
        "--input",
        type=str,
        default="results/tables/all_simulation_results.csv",
        help="Path to all_simulation_results.csv or a folder containing *_simulation_results.csv files.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results/analysis",
        help="Directory to save summary tables and plots.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = load_simulation_data(input_path)
    df = add_derived_columns(df)

    all_cases_summary = summarize_all_cases(df)
    non_terminal_summary = summarize_non_terminal_cases_only(df)

    all_cases_pretty = percent_columns(
        all_cases_summary,
        ["completion_rate", "move_accuracy", "invalid_move_rate", "x_win_rate", "o_win_rate", "draw_rate"],
    )
    non_terminal_pretty = percent_columns(
        non_terminal_summary,
        ["completion_rate", "move_accuracy", "invalid_move_rate", "x_win_rate", "o_win_rate", "draw_rate"],
    ) if not non_terminal_summary.empty else non_terminal_summary

    # Save raw processed rows
    df.to_csv(output_dir / "simulation_rows_processed.csv", index=False)

    # Save CSV summaries
    all_cases_pretty.to_csv(output_dir / "summary_all_cases.csv", index=False)
    if not non_terminal_pretty.empty:
        non_terminal_pretty.to_csv(output_dir / "summary_non_terminal_cases.csv", index=False)

    # Save Markdown tables
    save_markdown_table(
        all_cases_pretty,
        output_dir / "summary_all_cases.md",
        "Simulation Summary (All Cases)",
    )

    if not non_terminal_pretty.empty:
        save_markdown_table(
            non_terminal_pretty,
            output_dir / "summary_non_terminal_cases.md",
            "Simulation Summary (Non-Terminal Cases Only)",
        )

    # Plots
    plot_metric_by_game(
        all_cases_summary,
        metric="completion_rate",
        ylabel="Completion Rate",
        output_path=output_dir / "plot_completion_rate.png",
    )
    plot_metric_by_game(
        all_cases_summary,
        metric="move_accuracy",
        ylabel="Move Accuracy",
        output_path=output_dir / "plot_move_accuracy.png",
    )
    plot_metric_by_game(
        all_cases_summary,
        metric="invalid_move_rate",
        ylabel="Invalid Move Rate",
        output_path=output_dir / "plot_invalid_move_rate.png",
    )
    plot_metric_by_game(
        all_cases_summary,
        metric="avg_completed_turns",
        ylabel="Average Completed Turns",
        output_path=output_dir / "plot_avg_completed_turns.png",
    )
    plot_stacked_outcomes(
        all_cases_summary,
        output_path=output_dir / "plot_outcomes_stacked.png",
    )

    print("\nSaved analysis to:")
    print(output_dir.resolve())
    print("\nFiles:")
    print("- simulation_rows_processed.csv")
    print("- summary_all_cases.csv")
    print("- summary_all_cases.md")
    if not non_terminal_summary.empty:
        print("- summary_non_terminal_cases.csv")
        print("- summary_non_terminal_cases.md")
    print("- plot_completion_rate.png")
    print("- plot_move_accuracy.png")
    print("- plot_invalid_move_rate.png")
    print("- plot_avg_completed_turns.png")
    print("- plot_outcomes_stacked.png")


if __name__ == "__main__":
    main()