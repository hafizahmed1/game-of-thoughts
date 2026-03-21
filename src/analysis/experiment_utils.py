from __future__ import annotations

import json
import ast
import re
import pandas as pd
from pathlib import Path
from typing import Any, Optional

# --- SECTION 1: GENERAL PROJECT UTILITIES ---

def find_project_root(start: Path | None = None) -> Path:
    """Recursively searches upward for the project root containing 'src' and 'results'."""
    if start is None:
        start = Path().resolve()
    candidates = [start] + list(start.parents)
    for candidate in candidates:
        if (candidate / "src").exists() and (candidate / "results").exists():
            return candidate
    return Path().resolve()

# --- SECTION 2: RULE UNDERSTANDING & ERROR DETECTION ---

def evaluate_all_rule_detections(responses_error_dir: Path) -> pd.DataFrame:
    """Scans the rule_error_detection folder and calculates Precision/Recall/F1."""
    SUPPORTED_MODELS = ["llama-3.1-8b-instant", "qwen/qwen3-32b"]
    DEFAULT_GAMES = ["tictactoe", "connect_four"]

    summary_data = []
    detection_keywords = ["error", "invalid", "violation", "broken", "incorrect", "faulty", "wrong"]

    for model_id in SUPPORTED_MODELS:
        safe_model_name = model_id.replace("/", "_")
        for game in DEFAULT_GAMES:
            pattern = f"rule_error_detection_{game}_{safe_model_name}_*.txt"
            all_case_files = list(responses_error_dir.glob(pattern))
            if not all_case_files: continue
                
            tp, fn = 0, 0
            for file_path in all_case_files:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                detected = any(word in content for word in detection_keywords)
                if detected: tp += 1
                else: fn += 1
            
            precision = 1.0 if tp > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            summary_data.append({
                "model": model_id, "game": game, "precision": round(precision, 2),
                "recall": round(recall, 2), "f1": round(f1, 2), "cases": tp + fn
            })
    return pd.DataFrame(summary_data)

# --- SECTION 3: WIN EVALUATION LOGIC (THE FIX) ---

def check_cf_win(board: list[list[str]]) -> bool:
    """Corrected Connect Four Win Evaluator (6x7). Prevents boundary wrap."""
    rows, cols = 6, 7
    for r in range(rows):
        for c in range(cols):
            p = board[r][c]
            if p == ".": continue
            # Check 4 directions: Horizontal, Vertical, Diag-Down-Right, Diag-Down-Left
            if (c + 3 < cols and all(board[r][c+i] == p for i in range(4))) or \
               (r + 3 < rows and all(board[r+i][c] == p for i in range(4))) or \
               (r + 3 < rows and c + 3 < cols and all(board[r+i][c+i] == p for i in range(4))) or \
               (r + 3 < rows and c - 3 >= 0 and all(board[r+i][c-i] == p for i in range(4))):
                return True
    return False

# --- SECTION 4: SIMULATION & BOARD RECONSTRUCTION ---

def load_all_simulation_traces(project_root: Optional[Path] = None) -> list[dict]:
    root = find_project_root(project_root)
    simulation_dir = root / "results" / "responses" / "simulation"
    all_traces = []
    for trace_file in sorted(simulation_dir.glob("*.json")):
        try:
            with open(trace_file, "r", encoding="utf-8") as f:
                all_traces.extend(json.load(f))
        except: continue
    return all_traces

def parse_initial_board(case: dict, rows: int, cols: int) -> list[list[str]]:
    """Helper to ensure boards start with the setup provided to the LLM."""
    # If your JSON has a structured board, use it. Otherwise, return empty.
    # Adjust this if your JSON contains the initial grid state.
    return [["." for _ in range(cols)] for _ in range(rows)]

def reconstruct_ttt_boards(case: dict) -> list[tuple[str, str]]:
    board = parse_initial_board(case, 3, 3)
    states = [("Initial Setup", "\n".join(" | ".join(r) for r in board))]
    for turn in case.get("turns", []):
        player, move = turn.get("player"), str(turn.get("parsed_move_text"))
        try:
            r, c = ast.literal_eval(move.strip().strip("()"))
            board[r][c] = player
            states.append((f"Turn {turn['turn_index']} | {player} -> {r},{c}", "\n".join(" | ".join(r) for r in board)))
        except: states.append((f"INVALID: {move}", states[-1][1]))
    return states

def reconstruct_cf_boards(case: dict) -> list[tuple[str, str]]:
    board = parse_initial_board(case, 6, 7)
    states = [("Initial Setup", "\n".join(" ".join(r) for r in board))]
    for turn in case.get("turns", []):
        player, col = turn.get("player"), int(str(turn.get("parsed_move_text")).strip())
        placed = False
        for r in reversed(range(6)):
            if board[r][col] == ".":
                board[r][col] = player
                placed = True
                break
        label = f"Turn {turn['turn_index']} | {player} -> Col {col}"
        if not placed: label += " (FULL!)"
        states.append((label, "\n".join(" ".join(r) for r in board)))
    return states

def find_best_cases(traces):
    best_cases = {}
    for model in ["llama-3.1-8b-instant", "qwen/qwen3-32b"]:
        for game in ["tictactoe", "connect_four"]:
            matches = [t for t in traces if t['model'] == model and t['game'] == game and 
                       t.get('stopped_reason') == 'terminal_state_reached']
            if matches: best_cases[f"{model}_{game}"] = matches[0]
    return best_cases