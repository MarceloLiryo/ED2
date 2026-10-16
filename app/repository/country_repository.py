import json
from pathlib import Path
from typing import Any
import pandas as pd


class CountryRepository:
    """Responsável exclusivamente pela persistência dos dados de países."""

    def __init__(self, filepath: str | Path | None = None):
        if filepath is None:
            base_dir = Path(__file__).resolve().parent.parent
            self.filepath = base_dir / "data" / "countries.json"
        else:
            self.filepath = Path(filepath)

        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> list[dict[str, Any]]:
        if not self.filepath.exists():
            return []

        try:
            content = self.filepath.read_text(encoding="utf-8")
            data = json.loads(content)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def save_all(self, countries: list[dict[str, Any]]) -> None:
        content = json.dumps(countries, indent=4, ensure_ascii=False)
        self.filepath.write_text(content, encoding="utf-8")

    def to_dataframe(self) -> pd.DataFrame:
        """Prepara os dados persistidos em um DataFrame do Pandas para análises futuras."""
        data = self.load_all()
        if not data:
            return pd.DataFrame(columns=["code", "country", "region", "provider", "tech", "coordinates"])
        return pd.DataFrame(data)
