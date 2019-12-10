import pytest


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "model_label, key, expected_count",
    [
        ("fruits.love", "fruits_love", 8),
        ("fruits.joy", "fruits_joy", 16),
        ("fruits.peace", "fruits_peace", 32),
    ],
)
@pytest.mark.usefixtures("setup_teardown_fruits_models_schemas")
def test_models_and_schema(
    model_label, key, expected_count, all_concrete_fruits_models
):
    """
    Assert that models and schema are created.
    """
    model = all_concrete_fruits_models[key]
    assert model._default_manager.count() == 0
