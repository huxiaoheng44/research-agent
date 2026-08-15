from pathlib import Path

from bs4 import BeautifulSoup


class DocumentService:
    def load_text(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        
        if suffix in {".txt", ".md"}:
            return file_path.read_text(encoding="utf-8", errors="ignore")
        
        if suffix in {".html", ".htm"}:
            html = file_path.read_text(encoding="utf-8", errors="ignore")

            soup = BeautifulSoup(html, "html.parser")

            return soup.get_text(separator="\n", strip=True)

        raise ValueError(f"Unsupported file type: {suffix}")
        


    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")
        if overlap < 0:
            raise ValueError("overlap must be non-negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be less than chunk_size")

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunks.append(text[start:end].strip())
            start += chunk_size - overlap

        return chunks