from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


BASE_DIR = Path("results")
TABLES_DIR = BASE_DIR / "tables"
PLOTS_DIR = BASE_DIR / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def save_bar_plot(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    xlabel: str,
    ylabel: str,
    filename: str,
    hue_col: str | None = None,
) -> None:
    plt.figure(figsize=(10, 6))

    if df.empty:
        print(f"Skipping {filename}: empty dataframe")
        plt.close()
        return

    if hue_col is None:
        x_values = df[x_col].astype(str).tolist()
        y_values = df[y_col].fillna(0).tolist()
        plt.bar(x_values, y_values)
    else:
        x_values = [str(x) for x in sorted(df[x_col].dropna().unique())]
        hue_values = [str(h) for h in sorted(df[hue_col].dropna().unique())]

        if not x_values or not hue_values:
            print(f"Skipping {filename}: missing x or hue values")
            plt.close()
            return

        width = 0.8 / max(len(hue_values), 1)
        x_positions = list(range(len(x_values)))

        for i, hue in enumerate(hue_values):
            subset = df[df[hue_col].astype(str) == hue].copy()
            subset[x_col] = subset[x_col].astype(str)
            subset = subset.set_index(x_col).reindex(x_values).reset_index()

            values = subset[y_col].fillna(0).tolist()
            positions = [x + (i - (len(hue_values) - 1) / 2) * width for x in x_positions]

            plt.bar(positions, values, width=width, label=hue)

        plt.xticks(x_positions, x_values)

        handles, labels = plt.gca().get_legend_handles_labels()
        if handles:
            plt.legend(title=hue_col)

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved plot: {PLOTS_DIR / filename}")


def plot_move_simulation() -> None:
    path = TABLES_DIR / "move_simulation_results.csv"
    if not path.exists():
        print(f"Skipping move simulation plots: {path} not found")
        return

    df = pd.read_csv(path)

    required = {"game", "model", "completion_rate", "move_accuracy", "invalid_move_rate"}
    if not required.issubset(df.columns):
        print(f"Skipping move simulation plots: missing columns in {path}")
        print(f"Found columns: {df.columns.tolist()}")
        return

    save_bar_plot(
        df=df,
        x_col="game",
        y_col="completion_rate",
        hue_col="model",
        title="Move Simulation Completion Rate by Game and Model",
        xlabel="Game",
        ylabel="Completion Rate (%)",
        filename="move_completion_rate.png",
    )

    save_bar_plot(
        df=df,
        x_col="game",
        y_col="move_accuracy",
        hue_col="model",
        title="Move Simulation Accuracy by Game and Model",
        xlabel="Game",
        ylabel="Move Accuracy (%)",
        filename="move_accuracy.png",
    )

    save_bar_plot(
        df=df,
        x_col="game",
        y_col="invalid_move_rate",
        hue_col="model",
        title="Invalid Move Rate by Game and Model",
        xlabel="Game",
        ylabel="Invalid Move Rate (%)",
        filename="invalid_move_rate.png",
    )


def plot_rule_understanding() -> None:
    path = TABLES_DIR / "rule_understanding_results.csv"
    if not path.exists():
        print(f"Skipping rule understanding plots: {path} not found")
        return

    df = pd.read_csv(path)

    required = {"game", "model", "completeness"}
    if not required.issubset(df.columns):
        print(f"Skipping rule understanding plots: missing columns in {path}")
        print(f"Found columns: {df.columns.tolist()}")
        return

    save_bar_plot(
        df=df,
        x_col="game",
        y_col="completeness",
        hue_col="model",
        title="Rule Understanding Completeness by Game and Model",
        xlabel="Game",
        ylabel="Completeness Score",
        filename="rule_understanding_completeness.png",
    )


def plot_rule_error_detection() -> None:
    path = TABLES_DIR / "rule_error_results.csv"
    if not path.exists():
        print(f"Skipping rule error plots: {path} not found")
        return

    df = pd.read_csv(path)

    required = {"game", "model", "precision", "recall", "f1"}
    if not required.issubset(df.columns):
        print(f"Skipping rule error plots: missing columns in {path}")
        print(f"Found columns: {df.columns.tolist()}")
        return

    save_bar_plot(
        df=df,
        x_col="game",
        y_col="precision",
        hue_col="model",
        title="Rule Error Detection Precision by Game and Model",
        xlabel="Game",
        ylabel="Precision",
        filename="rule_error_precision.png",
    )

    save_bar_plot(
        df=df,
        x_col="game",
        y_col="recall",
        hue_col="model",
        title="Rule Error Detection Recall by Game and Model",
        xlabel="Game",
        ylabel="Recall",
        filename="rule_error_recall.png",
    )

    save_bar_plot(
        df=df,
        x_col="game",
        y_col="f1",
        hue_col="model",
        title="Rule Error Detection F1 by Game and Model",
        xlabel="Game",
        ylabel="F1 Score",
        filename="rule_error_f1.png",
    )


def plot_game_generation() -> None:
    path = TABLES_DIR / "generation_results.csv"
    if not path.exists():
        print(f"Skipping generation plots: {path} not found")
        return

    df = pd.read_csv(path)

    required = {"model", "clarity", "consistency", "balance", "fun", "coverage"}
    if not required.issubset(df.columns):
        print(f"Skipping generation plots: missing columns in {path}")
        print(f"Found columns: {df.columns.tolist()}")
        return

    metric_specs = [
        ("clarity", "Clarity"),
        ("consistency", "Consistency"),
        ("balance", "Balance"),
        ("fun", "Fun Factor"),
        ("coverage", "Section Coverage"),
    ]

    for metric, label in metric_specs:
        save_bar_plot(
            df=df,
            x_col="model",
            y_col=metric,
            title=f"Game Generation {label} by Model",
            xlabel="Model",
            ylabel=label,
            filename=f"generation_{metric}.png",
        )


def main() -> None:
    plot_move_simulation()
    plot_rule_understanding()
    plot_rule_error_detection()
    plot_game_generation()
    print(f"Plots saved in: {PLOTS_DIR}")


if __name__ == "__main__":
    main()