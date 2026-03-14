from pathlib import Path
from docx import Document


def load_docx_text(path: str | Path) -> str:
    """
    Load a .docx file and return plain text with paragraph breaks preserved.
    """
    path = Path(path)
    doc = Document(path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def split_tictactoe_sections(text: str) -> dict:
    """
    Split the noisy Tic-Tac-Toe rulebook into rough sections.
    Assumes section headers like 'ERRATA' and 'FAQ'.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    core_rules = []
    errata = []
    faq = []

    section = "core"
    for line in lines:
        upper = line.upper()

        if upper == "ERRATA":
            section = "errata"
            continue

        if upper.startswith("FAQ"):
            section = "faq"
            continue

        if section == "core":
            core_rules.append(line)
        elif section == "errata":
            errata.append(line)
        else:
            faq.append(line)

    return {
        "raw_text": text,
        "core_rules": core_rules,
        "errata": errata,
        "faq": faq,
    }