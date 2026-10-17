import pytest
from app.models.hash_table import HashTable
from app.models.country import CountryModel
from app.repository.country_repository import CountryRepository


@pytest.fixture
def temp_repo(tmp_path):
    json_file = tmp_path / "test_countries.json"
    return CountryRepository(filepath=json_file)


@pytest.fixture
def model(temp_repo):
    return CountryModel(repository=temp_repo, capacity=7)


@pytest.fixture
def sample_br():
    return {
        "code": "BR",
        "country": "Brasil",
        "region": "América",
        "provider": "Vivo",
        "tech": "5G",
        "coordinates": [-14.235, -51.9253],
    }


def test_hash_table_insert_and_search():
    ht = HashTable(capacity=5)
    ht.put("br", {"pais": "Brasil"})
    assert ht.search("BR") == {"pais": "Brasil"}
    assert ht.size == 1
    assert ht.last_search_comparisons == 1


def test_hash_table_collision_handling():
    # Capacidade 1 força colisão em todas as inserções após a primeira
    ht = HashTable(capacity=1)
    ht.put("BR", "Brasil")
    ht.put("PT", "Portugal")
    ht.put("IT", "Itália")

    metrics = ht.get_metrics()
    assert metrics["size"] == 3
    assert metrics["total_collisions_events"] == 2
    assert metrics["active_collisions"] == 2
    assert ht.search("IT") == "Itália"
    assert ht.last_search_comparisons == 3


def test_model_create_and_get(model, sample_br):
    model.create("br", sample_br)
    result = model.get_by_code("BR")
    assert result is not None
    assert result["country"] == "Brasil"
    assert result["code"] == "BR"


def test_model_duplicate_raises_key_error(model, sample_br):
    model.create("BR", sample_br)
    with pytest.raises(KeyError):
        model.create("br", sample_br)


def test_model_invalid_fields_raise_value_error(model, sample_br):
    invalid = sample_br.copy()
    invalid["provider"] = "   "
    with pytest.raises(ValueError):
        model.create("BR", invalid)


def test_model_update_and_delete(model, sample_br):
    model.create("BR", sample_br)

    updated_data = sample_br.copy()
    updated_data["tech"] = "4G/5G DSS"
    model.update("br", updated_data)

    assert model.get_by_code("BR")["tech"] == "4G/5G DSS"

    model.delete("BR")
    assert model.get_by_code("BR") is None


def test_repository_persistence_and_reload(tmp_path, sample_br):
    json_file = tmp_path / "persisted.json"
    repo1 = CountryRepository(filepath=json_file)
    service1 = CountryModel(repository=repo1, capacity=11)
    service1.create("BR", sample_br)

    # Nova instância deve carregar os dados do JSON para a Tabela Hash em memória
    repo2 = CountryRepository(filepath=json_file)
    service2 = CountryModel(repository=repo2, capacity=11)
    loaded = service2.get_by_code("BR")

    assert loaded is not None
    assert loaded["country"] == "Brasil"
    df = repo2.to_dataframe()
    assert len(df) == 1
    assert df.iloc[0]["code"] == "BR"


def test_itinerary_package_recommendation(model, sample_br):
    model.create("BR", sample_br)
    model.create(
        "PT",
        {
            "code": "PT",
            "country": "Portugal",
            "region": "Europa",
            "provider": "MEO",
            "tech": "5G",
            "coordinates": [39.3, -8.2],
        },
    )

    rec = model.recommend_package_for_itinerary("PT, BR, XX")
    assert rec["valid"] is True
    assert len(rec["covered"]) == 2
    assert rec["uncovered"] == ["XX"]
    assert rec["recommended_package"]["name"] == "Global"
