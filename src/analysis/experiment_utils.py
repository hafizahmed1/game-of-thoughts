from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from IPython.display import Markdown, display

from src.config import SUPPORTED_MODELS, DEFAULT_GAMES


def find_project_root(start: Path | None = None) -> Path:
    if start is None:
        start = Path.cwd().resolve()

    for candidate in [start, *start.parents]:
        if (candidate / "src").exists() and (candidate / "results").exists():
            return candidate

    return start


def safe_model_name(model_id: str) -> str:
    return model_id.replace("/", "_")


def safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def safe_read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def ensure_tables_dir(project_root: Optional[Path] = None) -> Path:
    root = find_project_root(project_root)
    tables_dir = root / "results" / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    return tables_dir


def evaluate_all_rule_detections(responses_error_dir: Path) -> pd.DataFrame:
    summary_data: list[dict[str, Any]] = []
    detection_keywords = [
        "error",
        "invalid",
        "violation",
        "broken",
        "incorrect",
        "faulty",
        "wrong",
        "inconsistent",
        "missing",
        "illegal",
    ]

    for model_id in SUPPORTED_MODELS:
        model_safe = safe_model_name(model_id)

        for game in DEFAULT_GAMES:
            pattern = f"rule_error_detection_{game}_{model_safe}_*.txt"
            case_files = sorted(responses_error_dir.glob(pattern))
            if not case_files:
                continue

            tp, fn = 0, 0

            for file_path in case_files:
                content = file_path.read_text(encoding="utf-8", errors="ignore").lower()
                detected = any(word in content for word in detection_keywords)

                if detected:
                    tp += 1
                else:
                    fn += 1

            precision = 1.0 if tp > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (
                2 * precision * recall / (precision + recall)
                if (precision + recall) > 0
                else 0.0
            )

            summary_data.append(
                {
                    "model": model_id,
                    "game": game,
                    "precision": round(precision, 4),
                    "recall": round(recall, 4),
                    "f1": round(f1, 4),
                    "cases": tp + fn,
                }
            )

    return pd.DataFrame(summary_data)


def check_ttt_win(board: list[list[str]]) -> bool:
    for r in range(3):
        if board[r][0] != "." and board[r][0] == board[r][1] == board[r][2]:
            return True

    for c in range(3):
        if board[0][c] != "." and board[0][c] == board[1][c] == board[2][c]:
            return True

    if board[0][0] != "." and board[0][0] == board[1][1] == board[2][2]:
        return True

    if board[0][2] != "." and board[0][2] == board[1][1] == board[2][0]:
        return True

    return False


def check_cf_win(board: list[list[str]]) -> bool:
    rows, cols = 6, 7

    for r in range(rows):
        for c in range(cols):
            p = board[r][c]
            if p == ".":
                continue

            if c + 3 < cols and all(board[r][c + i] == p for i in range(4)):
                return True
            if r + 3 < rows and all(board[r + i][c] == p for i in range(4)):
                return True
            if r + 3 < rows and c + 3 < cols and all(board[r + i][c + i] == p for i in range(4)):
                return True
            if r + 3 < rows and c - 3 >= 0 and all(board[r + i][c - i] == p for i in range(4)):
                return True

    return False


def load_all_simulation_traces(project_root: Optional[Path] = None) -> list[dict[str, Any]]:
    root = find_project_root(project_root)
    simulation_dir = root / "results" / "responses" / "simulation"

    if not simulation_dir.exists():
        return []

    all_traces: list[dict[str, Any]] = []

    for trace_file in sorted(simulation_dir.glob("*.json")):
        try:
            data = json.loads(trace_file.read_text(encoding="utf-8"))
            if isinstance(data, list):
                all_traces.extend(data)
            elif isinstance(data, dict):
                all_traces.append(data)
        except Exception:
            continue

    return all_traces


def _normalize_cell(cell: str) -> str:
    cell = str(cell).strip()
    return cell if cell in {"X", "O", "."} else "."


def _extract_numbered_board_lines(raw: str) -> list[str]:
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    return [line for line in lines if ":" in line and line[0].isdigit()]


def _extract_pipe_board_lines(raw: str) -> list[str]:
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    out: list[str] = []

    for line in lines:
        if "|" in line and not line.lower().startswith("current player") and "0   1   2" not in line:
            out.append(line)

    return out


def parse_initial_board(case: dict[str, Any], rows: int, cols: int) -> list[list[str]]:
    empty = [["." for _ in range(cols)] for _ in range(rows)]

    raw = case.get("initial_board")
    if not isinstance(raw, str) or not raw.strip():
        turns = case.get("turns", [])
        if turns and isinstance(turns[0], dict):
            raw = turns[0].get("board_state", "")
        else:
            raw = case.get("board_state", "")

    if not isinstance(raw, str) or not raw.strip():
        return empty

    game = str(case.get("game", "")).strip().lower()
    board: list[list[str]] = []

    if game == "tictactoe":
        numbered_lines = _extract_numbered_board_lines(raw)

        for line in numbered_lines[:rows]:
            _, rhs = line.split(":", 1)
            cells = [_normalize_cell(cell) for cell in rhs.split("|")]
            cells = cells[:cols]
            while len(cells) < cols:
                cells.append(".")
            board.append(cells)

    elif game == "connect_four":
        numbered_lines = _extract_numbered_board_lines(raw)

        if numbered_lines:
            for line in numbered_lines[:rows]:
                _, rhs = line.split(":", 1)
                cells = [_normalize_cell(cell) for cell in rhs.split("|")]
                cells = cells[:cols]
                while len(cells) < cols:
                    cells.append(".")
                board.append(cells)
        else:
            pipe_lines = _extract_pipe_board_lines(raw)

            for line in pipe_lines[:rows]:
                cells = [_normalize_cell(cell) for cell in line.split("|")]
                cells = cells[:cols]
                while len(cells) < cols:
                    cells.append(".")
                board.append(cells)

    while len(board) < rows:
        board.append(["." for _ in range(cols)])

    return board[:rows]


def parse_board_text(board_text: str, game: str) -> list[list[str]]:
    if not isinstance(board_text, str) or not board_text.strip():
        return []

    game = str(game).strip().lower()
    lines = [line.strip() for line in board_text.splitlines() if line.strip()]
    rows: list[list[str]] = []

    if game == "tictactoe":
        for line in lines:
            if ":" in line and line[0].isdigit():
                _, rhs = line.split(":", 1)
                rows.append([_normalize_cell(cell) for cell in rhs.split("|")])

    elif game == "connect_four":
        numbered_lines = [line for line in lines if ":" in line and line[0].isdigit()]
        if numbered_lines:
            for line in numbered_lines:
                _, rhs = line.split(":", 1)
                rows.append([_normalize_cell(cell) for cell in rhs.split("|")])
        else:
            for line in lines:
                if "|" in line and not line.lower().startswith("current player") and "0   1   2" not in line:
                    rows.append([_normalize_cell(cell) for cell in line.split("|")])

    return rows


def board_to_block(board: list[list[str]]) -> str:
    if not board:
        return "_Board unavailable_"
    return "```\n" + "\n".join(" ".join(row) for row in board) + "\n```"


def get_turn_move_text(turn: dict[str, Any]) -> str:
    for key in ["move", "parsed_move_text", "parsed_move", "action", "raw_response"]:
        value = turn.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def _parse_ttt_move(move_text: str) -> tuple[int, int] | None:
    try:
        value = ast.literal_eval(move_text)
        if isinstance(value, tuple) and len(value) == 2:
            return int(value[0]), int(value[1])
        if isinstance(value, list) and len(value) == 2:
            return int(value[0]), int(value[1])
    except Exception:
        pass

    match = re.search(r"(-?\d+)\s*,\s*(-?\d+)", move_text)
    if match:
        return int(match.group(1)), int(match.group(2))

    return None


def _parse_cf_move(move_text: str) -> int | None:
    move_text = str(move_text).strip()

    try:
        return int(move_text)
    except Exception:
        pass

    match = re.search(r"-?\d+", move_text)
    if match:
        return int(match.group(0))

    return None


def reconstruct_ttt_boards(case: dict[str, Any]) -> list[tuple[str, str]]:
    board = parse_initial_board(case, 3, 3)
    states = [("Initial setup", "\n".join(" | ".join(row) for row in board))]

    for idx, turn in enumerate(case.get("turns", []), start=1):
        player = str(turn.get("player", "?")).strip()
        move_text = get_turn_move_text(turn)
        move = _parse_ttt_move(move_text)

        if move is None:
            label = f"Turn {idx}: invalid move format by {player} -> {move_text}"
            states.append((label, "\n".join(" | ".join(row) for row in board)))
            continue

        r, c = move

        if 0 <= r < 3 and 0 <= c < 3 and board[r][c] == ".":
            board[r][c] = player
            label = f"Turn {idx}: {player} -> ({r}, {c})"
        else:
            label = f"Turn {idx}: illegal move by {player} -> {move_text}"

        states.append((label, "\n".join(" | ".join(row) for row in board)))

    return states


def reconstruct_cf_boards(case: dict[str, Any]) -> list[tuple[str, str]]:
    board = parse_initial_board(case, 6, 7)
    states = [("Initial setup", "\n".join(" ".join(row) for row in board))]

    for idx, turn in enumerate(case.get("turns", []), start=1):
        player = str(turn.get("player", "?")).strip()
        move_text = get_turn_move_text(turn)
        col = _parse_cf_move(move_text)

        if col is None or not (0 <= col < 7):
            label = f"Turn {idx}: invalid move format by {player} -> {move_text}"
            states.append((label, "\n".join(" ".join(row) for row in board)))
            continue

        placed = False
        for r in range(5, -1, -1):
            if board[r][col] == ".":
                board[r][col] = player
                placed = True
                break

        if placed:
            label = f"Turn {idx}: {player} -> column {col}"
        else:
            label = f"Turn {idx}: illegal move by {player} -> column {col} full"

        states.append((label, "\n".join(" ".join(row) for row in board)))

    return states


def _board_string_to_grid(board_str: str, game: str) -> list[list[str]]:
    lines = [line.strip() for line in board_str.splitlines() if line.strip()]

    if game == "tictactoe":
        return [[cell.strip() for cell in line.split("|")] for line in lines]

    return [line.split() for line in lines]


def initial_board_has_win(case: dict[str, Any]) -> bool:
    game = str(case.get("game", "")).strip().lower()

    if game == "tictactoe":
        board = parse_initial_board(case, 3, 3)
        return check_ttt_win(board)

    if game == "connect_four":
        board = parse_initial_board(case, 6, 7)
        return check_cf_win(board)

    return False


def get_win_reached_turn(case: dict[str, Any]) -> int | None:
    game = str(case.get("game", "")).strip().lower()

    if game == "tictactoe":
        states = reconstruct_ttt_boards(case)
        for idx, (_, board_str) in enumerate(states):
            grid = _board_string_to_grid(board_str, game)
            if check_ttt_win(grid):
                return idx
        return None

    if game == "connect_four":
        states = reconstruct_cf_boards(case)
        for idx, (_, board_str) in enumerate(states):
            grid = _board_string_to_grid(board_str, game)
            if check_cf_win(grid):
                return idx
        return None

    return None


def audit_case_termination(case: dict[str, Any]) -> dict[str, Any]:
    win_turn = get_win_reached_turn(case)
    total_turns = len(case.get("turns", []))
    initial_win = initial_board_has_win(case)

    if win_turn is None:
        return {
            "case_id": case.get("case_id"),
            "game": case.get("game"),
            "model": case.get("model"),
            "initial_board_has_win": initial_win,
            "win_reached_turn": None,
            "total_turns": total_turns,
            "continued_after_win": False,
            "extra_turns_after_win": 0,
        }

    extra_turns = max(total_turns - win_turn, 0)

    return {
        "case_id": case.get("case_id"),
        "game": case.get("game"),
        "model": case.get("model"),
        "initial_board_has_win": initial_win,
        "win_reached_turn": win_turn,
        "total_turns": total_turns,
        "continued_after_win": extra_turns > 0,
        "extra_turns_after_win": extra_turns,
    }


def game_kept_playing_after_win(case: dict[str, Any]) -> dict[str, Any]:
    audit = audit_case_termination(case)
    return {
        "win_reached_turn": audit["win_reached_turn"],
        "total_turns": audit["total_turns"],
        "kept_playing": audit["continued_after_win"],
        "extra_turns_after_win": audit["extra_turns_after_win"],
        "initial_board_has_win": audit["initial_board_has_win"],
    }


def count_cases_continued_after_win(
    traces: list[dict[str, Any]],
    game: str | None = None,
    model: str | None = None,
) -> pd.DataFrame:
    rows = []

    for case in traces:
        if game is not None and case.get("game") != game:
            continue
        if model is not None and case.get("model") != model:
            continue

        rows.append(audit_case_termination(case))

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    summary = (
        df.groupby(["game", "model"], as_index=False)
        .agg(
            total_cases=("case_id", "count"),
            initial_win_cases=("initial_board_has_win", "sum"),
            continued_after_win_cases=("continued_after_win", "sum"),
            avg_extra_turns_after_win=("extra_turns_after_win", "mean"),
        )
    )

    summary["avg_extra_turns_after_win"] = summary["avg_extra_turns_after_win"].round(2)
    return summary.sort_values(["game", "model"]).reset_index(drop=True)


def get_cases_continued_after_win(
    traces: list[dict[str, Any]],
    game: str | None = None,
    model: str | None = None,
) -> pd.DataFrame:
    rows = []

    for case in traces:
        if game is not None and case.get("game") != game:
            continue
        if model is not None and case.get("model") != model:
            continue

        audit = audit_case_termination(case)
        if audit["continued_after_win"]:
            rows.append(audit)

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(
            ["game", "model", "extra_turns_after_win", "case_id"],
            ascending=[True, True, False, True],
        ).reset_index(drop=True)

    return df


def choose_short_clean_case(
    traces: list[dict[str, Any]],
    game: str | None = None,
    model: str | None = None,
    require_terminal: bool = True,
    prefer_no_extra_play_after_win: bool = True,
) -> dict[str, Any] | None:
    candidates = traces

    if game is not None:
        candidates = [t for t in candidates if t.get("game") == game]

    if model is not None:
        candidates = [t for t in candidates if t.get("model") == model]

    if require_terminal:
        candidates = [t for t in candidates if t.get("stopped_reason") == "terminal_state_reached"]

    cleaned: list[tuple[int, int, dict[str, Any]]] = []

    for case in candidates:
        audit = audit_case_termination(case)

        if audit["initial_board_has_win"]:
            continue

        penalty = 0
        if prefer_no_extra_play_after_win and audit["continued_after_win"]:
            penalty = 1

        total_turns = len(case.get("turns", []))
        cleaned.append((penalty, total_turns, case))

    if not cleaned:
        return None

    cleaned.sort(key=lambda x: (x[0], x[1]))
    return cleaned[0][2]


def get_clean_reconstruction_cases(
    traces: list[dict[str, Any]],
    max_cases_per_game: int = 1,
) -> dict[str, dict[str, Any]]:
    selected_cases: dict[str, dict[str, Any]] = {}

    for game in DEFAULT_GAMES:
        valid: list[dict[str, Any]] = []

        for case in traces:
            if case.get("game") != game:
                continue

            if case.get("stopped_reason") != "terminal_state_reached":
                continue

            audit = audit_case_termination(case)

            if audit["initial_board_has_win"]:
                continue
            if audit["continued_after_win"]:
                continue
            if audit["win_reached_turn"] is None:
                continue

            valid.append(case)

        if not valid:
            continue

        valid.sort(key=lambda c: len(c.get("turns", [])))
        selected_cases[game] = valid[0]

    return selected_cases


def compare_models_summary(
    traces: list[dict[str, Any]],
    save_csv: bool = False,
    project_root: Optional[Path] = None,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for model in SUPPORTED_MODELS:
        for game in DEFAULT_GAMES:
            subset = [t for t in traces if t.get("model") == model and t.get("game") == game]
            if not subset:
                continue

            total_cases = len(subset)
            completed = sum(t.get("stopped_reason") == "terminal_state_reached" for t in subset)
            invalid_stop = sum(t.get("stopped_reason") == "invalid_move" for t in subset)

            total_valid_turns = sum(int(t.get("valid_turns", 0) or 0) for t in subset)
            total_turns = sum(int(t.get("total_turns", 0) or 0) for t in subset)

            winners = [str(t.get("winner", "")).strip().upper() for t in subset]
            x_wins = sum(w == "X" for w in winners)
            o_wins = sum(w == "O" for w in winners)
            draws = sum(w in {"DRAW", "TIE", "NONE"} for w in winners)

            rows.append(
                {
                    "model": model,
                    "game": game,
                    "cases": total_cases,
                    "completed_games": completed,
                    "completion_rate": round(completed / total_cases, 4) if total_cases else 0.0,
                    "legal_move_rate": round(total_valid_turns / total_turns, 4) if total_turns else 0.0,
                    "avg_valid_turns": round(total_valid_turns / total_cases, 2) if total_cases else 0.0,
                    "avg_total_turns": round(total_turns / total_cases, 2) if total_cases else 0.0,
                    "x_win_rate": round(x_wins / total_cases, 4) if total_cases else 0.0,
                    "o_win_rate": round(o_wins / total_cases, 4) if total_cases else 0.0,
                    "draw_rate": round(draws / total_cases, 4) if total_cases else 0.0,
                    "invalid_stop_rate": round(invalid_stop / total_cases, 4) if total_cases else 0.0,
                }
            )

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["game", "model"]).reset_index(drop=True)

    if save_csv and not df.empty:
        tables_dir = ensure_tables_dir(project_root)
        df.to_csv(tables_dir / "simulation_model_summary.csv", index=False)

    return df


def find_best_cases(traces: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    best_cases: dict[str, dict[str, Any]] = {}

    for model in SUPPORTED_MODELS:
        for game in DEFAULT_GAMES:
            matches = [
                t
                for t in traces
                if t.get("model") == model
                and t.get("game") == game
                and t.get("stopped_reason") == "terminal_state_reached"
            ]

            if not matches:
                continue

            matches = sorted(
                matches,
                key=lambda t: (
                    int(t.get("valid_turns", 0) or 0),
                    -int(t.get("total_turns", 0) or 0),
                ),
                reverse=True,
            )

            best_cases[f"{model}_{game}"] = matches[0]

    return best_cases


def choose_case_examples(sim_df: pd.DataFrame) -> dict[str, pd.Series]:
    examples: dict[str, pd.Series] = {}

    success_df = sim_df[sim_df["stopped_reason"] == "terminal_state_reached"].copy()
    failure_df = sim_df[sim_df["stopped_reason"] == "invalid_move"].copy()

    if not success_df.empty:
        success_df = success_df.sort_values(["valid_turns", "total_turns"], ascending=[False, False])
        examples["success"] = success_df.iloc[0]

    if not failure_df.empty:
        failure_df = failure_df.sort_values(["valid_turns", "total_turns"], ascending=[False, False])
        examples["failure"] = failure_df.iloc[0]

    return examples


def _get_success_case(traces: list[dict[str, Any]], game: str) -> dict[str, Any] | None:
    valid = []

    for case in traces:
        if case.get("game") != game:
            continue
        if case.get("stopped_reason") != "terminal_state_reached":
            continue
        if len(case.get("turns", [])) < 4:
            continue
    
        audit = audit_case_termination(case)

        if audit.get("initial_board_has_win"):
            continue
        if audit.get("continued_after_win"):
            continue
        if audit.get("win_reached_turn") is None:
            continue

        valid.append(case)

    if not valid:
        return None

    valid.sort(key=lambda c: len(c.get("turns", [])))
    return valid[0]


def _get_failure_case(traces: list[dict[str, Any]], game: str) -> dict[str, Any] | None:
    candidates = []

    for case in traces:
        if case.get("game") != game:
            continue
        if case.get("stopped_reason") == "invalid_move":
            candidates.append(case)

    if not candidates:
        return None

    candidates.sort(key=lambda c: len(c.get("turns", [])), reverse=True)
    return candidates[0]


def _render_case(case: dict[str, Any] | None, game_name: str, success: bool = True) -> None:
    if case is None:
        display(Markdown(f"No case found for {game_name}."))
        return

    if case.get("game") == "connect_four":
        states = reconstruct_cf_boards(case)
    else:
        states = reconstruct_ttt_boards(case)

    status = "Successful" if success else "Failed"

    display(
        Markdown(
            f"### {game_name} ({status} Case)\n"
            f"**Case ID:** `{case.get('case_id')}`  \n"
            f"**Model:** `{case.get('model')}`  \n"
            f"**Stopped reason:** `{case.get('stopped_reason')}`  \n"
            f"**Winner:** `{case.get('winner')}`  \n"
            f"**Turns:** `{len(case.get('turns', []))}`"
        )
    )

    content = ""
    for label, board in states:
        content += f"#### {label}\n"
        content += "```\n" + board + "\n```\n\n"

    display(
        Markdown(
            f"""
<details>
<summary>Show board progression</summary>

{content}

</details>
"""
        )
    )


def show_simulation_cases(traces: list[dict[str, Any]]) -> None:
    cf_success = _get_success_case(traces, "connect_four")
    cf_failure = _get_failure_case(traces, "connect_four")

    _render_case(cf_success, "Connect Four", success=True)
    _render_case(cf_failure, "Connect Four", success=False)

    ttt_success = _get_success_case(traces, "tictactoe")
    ttt_failure = _get_failure_case(traces, "tictactoe")

    _render_case(ttt_success, "Tic-Tac-Toe", success=True)
    _render_case(ttt_failure, "Tic-Tac-Toe", success=False)