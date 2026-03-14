import json
import sys
from pathlib import Path

# Add repo root to Python path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.rule_loader import load_docx_text, split_tictactoe_sections

RAW_PATH = ROOT / "data" / "raw" / "TIC_TAC_TOE_RULES.docx"
OUT_PATH = ROOT / "data" / "processed" / "tictactoe_rulebook.json"


def main() -> None:
    text = load_docx_text(RAW_PATH)
    parsed = split_tictactoe_sections(text)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2, ensure_ascii=False)

    print(f"Saved processed rulebook to: {OUT_PATH}")


if __name__ == "__main__":
    main()