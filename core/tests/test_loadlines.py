from django.core.management import call_command
from django.core.management.base import CommandError

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


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "model_label, key", [("fruits.fixtureless", "fruits_fixtureless")]
)
@pytest.mark.usefixtures("setup_teardown_fruits_models_schemas", "mock_open")
def test_loadlines_for_fixtureless_models(
    model_label, key, all_concrete_fruits_models, stringIO
):
    """
    Assert that `loadlines` throws appropriate command error
    when an attempt is made to use it to populate model without
    corresponding JSON Lines fixtures file.
    """
    model = all_concrete_fruits_models[key]
    assert model._default_manager.count() == 0

    with pytest.raises(CommandError) as e:
        call_command("loadlines", model_label, stdout=stringIO)

    assert "Fixtures file not found" in str(e.value)
    assert model._default_manager.count() == 0
