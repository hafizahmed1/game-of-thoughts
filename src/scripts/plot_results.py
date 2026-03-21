import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# --- PATH SETUP ---
BASE_DIR = Path(__file__).resolve().parents[2]
RESPONSES_DIR = BASE_DIR / "results" / "responses"
PLOTS_DIR = BASE_DIR / "results" / "plots"

PLOTS_DIR.mkdir(parents=True, exist_ok=True)

def save_multi_metric_plot(
    df: pd.DataFrame, 
    x_col: str, 
    metrics_map: dict[str, str], 
    hue_col: str, 
    title: str, 
    filename: str
):
    """
    Creates a single figure with subplots for each metric.
    metrics_map: {csv_column_name: display_label}
    """
    if df.empty:
        print(f"Skipping {filename}: empty dataframe")
        return

    metrics = list(metrics_map.keys())
    num_metrics = len(metrics)
    
    # Create subplots (1 row, N columns)
    fig, axes = plt.subplots(1, num_metrics, figsize=(5 * num_metrics, 5), sharey=True)
    
    if num_metrics == 1:
        axes = [axes]

    for i, metric in enumerate(metrics):
        ax = axes[i]
        # Pivot the data: Games as rows, Models as columns
        pivot_df = df.pivot_table(index=x_col, columns=hue_col, values=metric, aggfunc='mean')
        
        pivot_df.plot(kind='bar', ax=ax, width=0.8, legend=False)
        
        ax.set_title(metrics_map[metric], fontsize=12, fontweight='bold')
        ax.set_xlabel(x_col.title())
        ax.set_ylabel("Score (0-1)" if i == 0 else "")
        ax.set_ylim(0, 1.05) # Standardize scale for comparison
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        ax.tick_params(axis='x', rotation=45)

    # Add a single legend for the whole figure
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, title=hue_col, loc='center right', bbox_to_anchor=(1.05, 0.5))

    plt.suptitle(title, fontsize=16, fontweight='bold', y=1.05)
    plt.tight_layout()
    
    save_path = PLOTS_DIR / filename
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✅ Saved multi-metric plot: {save_path}")


def plot_rule_understanding():
    path = RESPONSES_DIR / "rule_understanding" / "rule_understanding_results.csv"
    if not path.exists():
        print(f"Skipping rule understanding: {path} not found")
        return

    df = pd.read_csv(path)
    # Mapping completeness to 'Recall' as requested
    metrics = {
        "precision": "Precision",
        "completeness": "Recall",
        "f1": "F1 Score"
    }
    
    save_multi_metric_plot(
        df=df, x_col="game", metrics_map=metrics, hue_col="model",
        title="Rule Understanding: Performance Metrics",
        filename="summary_rule_understanding_combined.png"
    )


def plot_rule_error_detection():
    path = RESPONSES_DIR / "rule_error_detection" / "rule_error_results.csv"
    if not path.exists():
        print(f"Skipping rule error: {path} not found")
        return

    df = pd.read_csv(path)
    metrics = {
        "precision": "Precision",
        "recall": "Recall",
        "f1": "F1 Score"
    }
    
    save_multi_metric_plot(
        df=df, x_col="game", metrics_map=metrics, hue_col="model",
        title="Rule Error Detection: Performance Metrics",
        filename="summary_rule_error_combined.png"
    )


def plot_game_generation():
    path = RESPONSES_DIR / "game_generation" / "generation_results.csv"
    if not path.exists():
        print(f"Skipping generation: {path} not found")
        return

    df = pd.read_csv(path)
    # Just Clarity for generation summary
    save_multi_metric_plot(
        df=df, x_col="model", metrics_map={"clarity": "Clarity"}, hue_col=None,
        title="Game Generation Quality",
        filename="summary_generation_clarity.png"
    )


def main():
    print("📊 Generating multi-metric summary plots...")
    plot_rule_understanding()
    plot_rule_error_detection()
    plot_game_generation()
    print(f"\n🚀 All plots saved in: {PLOTS_DIR}")


if __name__ == "__main__":
    main()