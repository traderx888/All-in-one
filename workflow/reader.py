"""Read articles and reports from local files.

Supported formats: .pdf, .docx, .txt, .md, .html
"""

from pathlib import Path
from dataclasses import dataclass

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md", ".html", ".htm"}


@dataclass
class Article:
    title: str
    body: str
    source_path: str


def read_file(path: Path) -> str:
    ext = path.suffix.lower()

    if ext == ".pdf":
        return _read_pdf(path)
    if ext in (".docx", ".doc"):
        return _read_docx(path)
    if ext in (".html", ".htm"):
        return _read_html(path)
    # .txt, .md — plain text
    return path.read_text(encoding="utf-8", errors="replace")


def _read_pdf(path: Path) -> str:
    from PyPDF2 import PdfReader

    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages)


def _read_docx(path: Path) -> str:
    from docx import Document

    doc = Document(str(path))
    return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())


def _read_html(path: Path) -> str:
    from bs4 import BeautifulSoup

    html = path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")
    # Remove script / style tags
    for tag in soup(["script", "style"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def load_articles(input_dir: Path) -> list[Article]:
    """Scan *input_dir* and return an Article for every supported file."""
    articles: list[Article] = []
    if not input_dir.exists():
        return articles

    for fpath in sorted(input_dir.iterdir()):
        if fpath.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        try:
            body = read_file(fpath)
            if not body.strip():
                continue
            articles.append(
                Article(
                    title=fpath.stem.replace("_", " ").replace("-", " ").title(),
                    body=body,
                    source_path=str(fpath),
                )
            )
        except Exception as exc:
            print(f"  [warning] Skipping {fpath.name}: {exc}")
    return articles
