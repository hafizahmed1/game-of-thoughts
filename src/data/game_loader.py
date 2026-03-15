from pathlib import Path
from docx import Document
from pypdf import PdfReader


def read_txt(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")


def read_docx(file_path: Path) -> str:
    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def read_pdf(file_path: Path) -> str:
    reader = PdfReader(file_path)
    text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)
    return "\n".join(text)


def read_rules_file(file_path: Path) -> str:
    if file_path.suffix == ".txt":
        return read_txt(file_path)

    if file_path.suffix == ".docx":
        return read_docx(file_path)

    if file_path.suffix == ".pdf":
        return read_pdf(file_path)

    raise ValueError(f"Unsupported rules format: {file_path}")


def find_rules_file(game_folder: Path) -> Path:
    for ext in ["txt", "docx", "pdf"]:
        path = game_folder / f"rules.{ext}"
        if path.exists():
            return path

    raise FileNotFoundError(f"No rules file found in {game_folder}")


def load_game_data(game_slug: str) -> dict:
    base = Path("data/raw") / game_slug

    rules_file = find_rules_file(base)
    rules_text = read_rules_file(rules_file)

    broken_rules_text = None
    for ext in ["txt", "docx", "pdf"]:
        broken_file = base / f"broken_rules.{ext}"
        if broken_file.exists():
            broken_rules_text = read_rules_file(broken_file)
            break

    return {
        "rules_text": rules_text,
        "broken_rules_text": broken_rules_text,
    }