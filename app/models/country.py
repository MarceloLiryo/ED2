from typing import Any, TypedDict
from app.models.hash_table import HashTable
from app.repository.country_repository import CountryRepository


class CountryRecord(TypedDict):
    code: str
    country: str
    region: str
    provider: str
    tech: str
    coordinates: list[float]


class CountryModel:
    """
    Gerencia os países atendidos em memória através da Tabela Hash
    e sincroniza as alterações com o CountryRepository.
    """

    def __init__(self, repository: CountryRepository | None = None, capacity: int = 11):
        self.hash_table = HashTable(capacity=capacity)
        self.repository = repository or CountryRepository()
        self._load_initial_data()

    def _load_initial_data(self) -> None:
        records = self.repository.load_all()
        for item in records:
            code = str(item.get("code", "")).strip().upper()
            if code and code not in self.hash_table:
                normalized_item = self._validate_and_format(code, item)
                self.hash_table.put(code, normalized_item)

    def _sync_repository(self) -> None:
        all_countries = self.list_all()
        self.repository.save_all(all_countries)

    def _validate_and_format(self, code: str, data: dict[str, Any]) -> CountryRecord:
        clean_code = code.strip().upper()
        if not clean_code or len(clean_code) < 2 or len(clean_code) > 3:
            raise ValueError("O código do país deve ter 2 ou 3 letras (ex: BR, IT, US).")

        country_name = str(data.get("country", "")).strip()
        region = str(data.get("region") or data.get("continent") or "").strip()
        provider = str(data.get("provider", "")).strip()
        tech = str(data.get("tech", "")).strip()

        if not all([country_name, region, provider, tech]):
            raise ValueError("Todos os campos obrigatórios (país, região, operadora e tecnologia) devem ser preenchidos.")

        coords = data.get("coordinates")
        if isinstance(coords, (list, tuple)) and len(coords) == 2:
            lat, lng = float(coords[0]), float(coords[1])
        else:
            lat = float(data.get("lat", 0.0) or 0.0)
            lng = float(data.get("lng", 0.0) or 0.0)

        return {
            "code": clean_code,
            "country": country_name,
            "region": region,
            "provider": provider,
            "tech": tech,
            "coordinates": [lat, lng],
        }


    def create(self, code: str, data: dict[str, Any]) -> CountryRecord:
        record = self._validate_and_format(code, data)
        self.hash_table.put(record["code"], record)
        self._sync_repository()
        return record

    def get_by_code(self, code: str) -> CountryRecord | None:
        return self.hash_table.search(code)

    def list_all(self) -> list[CountryRecord]:
        items = self.hash_table.values()
        return sorted(items, key=lambda x: x["country"].lower())

    def update(self, code: str, data: dict[str, Any]) -> CountryRecord:
        record = self._validate_and_format(code, data)
        self.hash_table.update(record["code"], record)
        self._sync_repository()
        return record

    def delete(self, code: str) -> CountryRecord:
        removed = self.hash_table.remove(code)
        self._sync_repository()
        return removed

    def get_instrumentation(self) -> dict[str, Any]:
        return self.hash_table.get_metrics()



    def recommend_package_for_itinerary(self, codes_raw: str) -> dict[str, Any]:
        """
        Diferencial da Equipe (Prévia na Etapa 1):
        Recebe uma sequência de códigos de países (ex: 'PT, ES, FR'), consulta cada país na Tabela Hash e recomenda o pacote ideal.
        """
        codes = [c.strip().upper() for c in codes_raw.replace(";", ",").split(",") if c.strip()]
        if not codes:
            return {"valid": False, "error": "Informe ao menos um código de país."}

        covered: list[CountryRecord] = []
        uncovered: list[str] = []
        total_comparisons = 0

        for code in codes:
            found = self.get_by_code(code)
            total_comparisons += self.hash_table.last_search_comparisons
            if found:
                covered.append(found)
            else:
                uncovered.append(code)

        regions = {item["region"].lower() for item in covered}
        num_stops = len(covered)

        if not covered:
            package = None
        elif len(regions) == 1 and "europa" in next(iter(regions)):
            package = (
                {"code": 101, "name": "Europa Basic", "data": "5 GB", "validity": "15 dias"}
                if num_stops <= 2
                else {"code": 102, "name": "Europa Plus", "data": "10 GB", "validity": "30 dias"}
            )
        elif len(regions) == 1 and ("américa" in next(iter(regions)) or "america" in next(iter(regions))):
            package = (
                {"code": 201, "name": "América Basic", "data": "5 GB", "validity": "15 dias"}
                if num_stops <= 2
                else {"code": 202, "name": "América Plus", "data": "15 GB", "validity": "30 dias"}
            )
        else:
            package = {"code": 301, "name": "Global", "data": "20 GB", "validity": "30 dias"}

        return {
            "valid": True,
            "requested_codes": codes,
            "covered": covered,
            "uncovered": uncovered,
            "total_hash_comparisons": total_comparisons,
            "recommended_package": package,
        }


country_service = CountryModel()
