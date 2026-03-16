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


def find_first_matching_file(folder: Path, stem: str):
    for ext in ["txt", "docx", "pdf"]:
        path = folder / f"{stem}.{ext}"
        if path.exists():
            return path
    return None


def load_game_data(game_slug: str) -> dict:
    base = Path("data/raw") / game_slug

    rules_file = find_first_matching_file(base, "rules")
    if rules_file is None:
        raise FileNotFoundError(f"No rules file found in {base}")

    broken_rules_file = find_first_matching_file(base, "broken_rules")

    return {
        "rules_text": read_rules_file(rules_file),
        "broken_rules_text": read_rules_file(broken_rules_file) if broken_rules_file else None,
    }