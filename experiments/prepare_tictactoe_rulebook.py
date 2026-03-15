import json
import sys
from pathlib import Path

# Add repo root to Python path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.rule_loader import load_docx_text, split_tictactoe_sections
from src.utils.helpers import get_provider, get_model_name

RAW_PATH = ROOT / "data" / "raw" / "TIC_TAC_TOE_RULES.docx"
OUT_PATH = ROOT / "data" / "processed" / "tictactoe_rulebook.json"
BROKEN_PATH = ROOT / "data" / "processed" / "broken_tic_tac_toe.txt" # Match the script's expectation

def main() -> None:
    # 1. Process standard rulebook
    text = load_docx_text(RAW_PATH)
    parsed = split_tictactoe_sections(text)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2, ensure_ascii=False)
    print(f"Saved processed rulebook to: {OUT_PATH}")

    # 2. Generate the missing broken rules file
    # We create a version of the rules with a logical error (e.g., 4 in a row)
    broken_content = text.replace("three in a row", "four in a row")
    BROKEN_PATH.write_text(broken_content, encoding="utf-8")
    print(f"Saved broken rules to: {BROKEN_PATH}")


if __name__ == "__main__":
    main()