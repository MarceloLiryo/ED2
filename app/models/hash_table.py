from typing import Any


class HashNode:
    """Nó interno para armazenar o par (chave, valor) dentro de um bucket."""

    def __init__(self, key: str, value: Any):
        self.key: str = key
        self.value: Any = value


class HashTable:
    """
    Tabela Hash com tratamento de colisões por encadeamento externo (buckets).
    Inclui instrumentação para observar colisões, fator de carga e comparações.
    """

    def __init__(self, capacity: int = 11):
        if capacity <= 0:
            raise ValueError("A capacidade da Tabela Hash deve ser maior que zero.")
        self.capacity: int = capacity
        self.buckets: list[list[HashNode]] = [[] for _ in range(capacity)]
        self.size: int = 0
        self.collisions: int = 0
        self.last_search_comparisons: int = 0

    def _normalize(self, key: str) -> str:
        if not isinstance(key, str) or not key.strip():
            raise ValueError("A chave deve ser uma string não vazia.")
        return key.strip().upper()

    def _hash_function(self, key: str) -> int:
        """Calcula o índice do bucket usando espalhamento polinomial (base 37)."""
        normalized = self._normalize(key)
        acc = 0
        for position, char in enumerate(normalized, start=1):
            acc = (acc * 37 + ord(char) * position) % self.capacity
        return acc

    def put(self, key: str, value: Any) -> None:
        """Insere um novo elemento na Tabela Hash. Lança KeyError se a chave já existir."""
        norm_key = self._normalize(key)
        bucket_idx = self._hash_function(norm_key)
        bucket = self.buckets[bucket_idx]

        for node in bucket:
            if node.key == norm_key:
                raise KeyError(f"O código '{norm_key}' já está cadastrado na Tabela Hash.")

        if len(bucket) > 0:
            self.collisions += 1

        bucket.append(HashNode(norm_key, value))
        self.size += 1

    def search(self, key: str) -> Any | None:
        """Busca um elemento pela chave e registra o número de comparações realizadas."""
        if not isinstance(key, str) or not key.strip():
            self.last_search_comparisons = 0
            return None

        norm_key = self._normalize(key)
        bucket_idx = self._hash_function(norm_key)
        bucket = self.buckets[bucket_idx]

        comparisons = 0
        for node in bucket:
            comparisons += 1
            if node.key == norm_key:
                self.last_search_comparisons = comparisons
                return node.value

        self.last_search_comparisons = comparisons
        return None

    def update(self, key: str, value: Any) -> None:
        """Atualiza o valor associado a uma chave existente."""
        norm_key = self._normalize(key)
        bucket_idx = self._hash_function(norm_key)
        bucket = self.buckets[bucket_idx]

        for node in bucket:
            if node.key == norm_key:
                node.value = value
                return

        raise KeyError(f"O código '{norm_key}' não foi encontrado para atualização.")

    def remove(self, key: str) -> Any:
        """Remove uma chave da Tabela Hash e retorna seu valor."""
        norm_key = self._normalize(key)
        bucket_idx = self._hash_function(norm_key)
        bucket = self.buckets[bucket_idx]

        for idx, node in enumerate(bucket):
            if node.key == norm_key:
                removed = bucket.pop(idx)
                self.size -= 1
                return removed.value

        raise KeyError(f"O código '{norm_key}' não foi encontrado para remoção.")

    def values(self) -> list[Any]:
        """Retorna todos os valores armazenados percorrendo os buckets."""
        result: list[Any] = []
        for bucket in self.buckets:
            for node in bucket:
                result.append(node.value)
        return result

    def get_metrics(self) -> dict[str, Any]:
        """Retorna dados de instrumentação da Tabela Hash para exibição na interface."""
        used_buckets = sum(1 for b in self.buckets if len(b) > 0)
        active_collisions = sum(len(b) - 1 for b in self.buckets if len(b) > 1)

        return {
            "capacity": self.capacity,
            "size": self.size,
            "load_factor": round(self.size / self.capacity, 2),
            "total_collisions_events": self.collisions,
            "active_collisions": active_collisions,
            "used_buckets": used_buckets,
            "last_search_comparisons": self.last_search_comparisons,
            "buckets": [
                {
                    "index": idx,
                    "count": len(bucket),
                    "has_collision": len(bucket) > 1,
                    "keys": [node.key for node in bucket],
                    "items": [node.value for node in bucket],
                }
                for idx, bucket in enumerate(self.buckets)
            ],
        }

    def __contains__(self, key: str) -> bool:
        return self.search(key) is not None

    def __getitem__(self, key: str) -> Any:
        val = self.search(key)
        if val is None:
            raise KeyError(key)
        return val
