from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = ROOT / "results" / "tables"
FIGURES_DIR = ROOT / "results" / "figures"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def load_simulation_data(csv_path: str | None = None) -> pd.DataFrame:
    path = Path(csv_path) if csv_path else TABLES_DIR / "all_simulation_results.csv"

    if not path.exists():
        raise FileNotFoundError(f"Simulation results file not found: {path}")

    df = pd.read_csv(path)

    required_columns = {
        "game",
        "model",
        "completed_turns",
        "stopped_reason",
        "winner",
        "total_turns",
        "valid_turns",
        "invalid_turns",
    }

    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in simulation CSV: {sorted(missing)}")

    return df


def prepare_metrics(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby(["model", "game"], as_index=False)
        .agg(
            total_cases=("case_id", "count"),
            total_turns=("total_turns", "sum"),
            valid_turns=("valid_turns", "sum"),
            invalid_turns=("invalid_turns", "sum"),
            avg_completed_turns=("completed_turns", "mean"),
            terminal_cases=("stopped_reason", lambda s: (s == "terminal_state_reached").sum()),
        )
    )

    summary["valid_move_rate"] = summary["valid_turns"] / summary["total_turns"]
    summary["invalid_move_rate"] = summary["invalid_turns"] / summary["total_turns"]
    summary["terminal_completion_rate"] = summary["terminal_cases"] / summary["total_cases"]

    return summary


def save_grouped_bar(
    data: pd.DataFrame,
    value_col: str,
    title: str,
    ylabel: str,
    output_path: Path,
) -> None:
    pivot = data.pivot(index="game", columns="model", values=value_col)

    ax = pivot.plot(kind="bar", figsize=(8, 5))
    ax.set_title(title)
    ax.set_xlabel("Game")
    ax.set_ylabel(ylabel)
    ax.legend(title="Model")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()


def save_model_bar(
    data: pd.DataFrame,
    value_col: str,
    title: str,
    ylabel: str,
    output_path: Path,
) -> None:
    aggregated = (
        data.groupby("model", as_index=False)[value_col]
        .mean()
        .sort_values(value_col, ascending=False)
    )

    ax = aggregated.plot(kind="bar", x="model", y=value_col, legend=False, figsize=(7, 5))
    ax.set_title(title)
    ax.set_xlabel("Model")
    ax.set_ylabel(ylabel)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()


def save_stopped_reason_chart(df: pd.DataFrame, output_path: Path) -> None:
    counts = (
        df.groupby(["model", "stopped_reason"])
        .size()
        .unstack(fill_value=0)
    )

    ax = counts.plot(kind="bar", figsize=(9, 5))
    ax.set_title("Simulation Stop Reasons by Model")
    ax.set_xlabel("Model")
    ax.set_ylabel("Number of Cases")
    ax.legend(title="Stop Reason")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()


def save_winner_chart(df: pd.DataFrame, output_path: Path) -> None:
    winner_df = df.copy()
    winner_df["winner"] = winner_df["winner"].fillna("none")

    counts = (
        winner_df.groupby(["model", "winner"])
        .size()
        .unstack(fill_value=0)
    )

    ax = counts.plot(kind="bar", figsize=(9, 5))
    ax.set_title("Game Outcomes by Model")
    ax.set_xlabel("Model")
    ax.set_ylabel("Number of Cases")
    ax.legend(title="Winner")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()


def save_summary_table(summary: pd.DataFrame, output_path: Path) -> None:
    table = summary.copy()

    for col in ["valid_move_rate", "invalid_move_rate", "terminal_completion_rate"]:
        table[col] = (table[col] * 100).round(2)

    table["avg_completed_turns"] = table["avg_completed_turns"].round(2)

    table = table[
        [
            "model",
            "game",
            "total_cases",
            "total_turns",
            "valid_turns",
            "invalid_turns",
            "valid_move_rate",
            "invalid_move_rate",
            "avg_completed_turns",
            "terminal_cases",
            "terminal_completion_rate",
        ]
    ]

    table.to_csv(output_path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create report-quality figures from simulation results.")
    parser.add_argument(
        "--csv",
        default=None,
        help="Optional path to simulation CSV. Defaults to results/tables/all_simulation_results.csv",
    )
    args = parser.parse_args()

    df = load_simulation_data(args.csv)
    summary = prepare_metrics(df)

    save_summary_table(summary, TABLES_DIR / "simulation_report_summary.csv")

    save_model_bar(
        summary,
        value_col="valid_move_rate",
        title="Average Valid Move Rate by Model",
        ylabel="Valid Move Rate",
        output_path=FIGURES_DIR / "valid_move_rate_by_model.png",
    )

    save_model_bar(
        summary,
        value_col="invalid_move_rate",
        title="Average Invalid Move Rate by Model",
        ylabel="Invalid Move Rate",
        output_path=FIGURES_DIR / "invalid_move_rate_by_model.png",
    )

    save_model_bar(
        summary,
        value_col="avg_completed_turns",
        title="Average Completed Turns by Model",
        ylabel="Average Completed Turns",
        output_path=FIGURES_DIR / "average_completed_turns_by_model.png",
    )

    save_model_bar(
        summary,
        value_col="terminal_completion_rate",
        title="Average Terminal Completion Rate by Model",
        ylabel="Terminal Completion Rate",
        output_path=FIGURES_DIR / "terminal_completion_rate_by_model.png",
    )

    save_grouped_bar(
        summary,
        value_col="valid_move_rate",
        title="Valid Move Rate by Game and Model",
        ylabel="Valid Move Rate",
        output_path=FIGURES_DIR / "valid_move_rate_by_game_and_model.png",
    )

    save_grouped_bar(
        summary,
        value_col="avg_completed_turns",
        title="Average Completed Turns by Game and Model",
        ylabel="Average Completed Turns",
        output_path=FIGURES_DIR / "average_completed_turns_by_game_and_model.png",
    )

    save_grouped_bar(
        summary,
        value_col="terminal_completion_rate",
        title="Terminal Completion Rate by Game and Model",
        ylabel="Terminal Completion Rate",
        output_path=FIGURES_DIR / "terminal_completion_rate_by_game_and_model.png",
    )

    save_stopped_reason_chart(
        df,
        FIGURES_DIR / "stopped_reasons_by_model.png",
    )

    save_winner_chart(
        df,
        FIGURES_DIR / "outcomes_by_model.png",
    )

    print(f"Saved report summary table to: {TABLES_DIR / 'simulation_report_summary.csv'}")
    print(f"Saved figures to: {FIGURES_DIR}")


if __name__ == "__main__":
    main()