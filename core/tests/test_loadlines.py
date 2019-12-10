from django.core.management import call_command

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
@pytest.mark.usefixtures("setup_teardown_fruits_models_schemas", "mock_open")
def test_loadlines(
    model_label, key, expected_count, all_concrete_fruits_models, stringIO
):
    """
    Assert that `loadlines` populates the correct model with
    the appropriate JSON Lines fixtures.
    """
    model = all_concrete_fruits_models[key]
    assert model._default_manager.count() == 0

    call_command("loadlines", model_label, stdout=stringIO)
    assert model._default_manager.count() == expected_count
    assert (
        stringIO.getvalue().strip()
        == f"Created: {expected_count} objects of the model {model._meta.label}"
    )
