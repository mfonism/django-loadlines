import copy
import pathlib

from django.core.management import call_command
from django.core.management.base import CommandError

import pytest


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "model_label, key, expected_count",
    [
        ("fruits.love", "fruits_love", 8),
        ("fruits.Love", "fruits_love", 8),
        ("fruits.joy", "fruits_joy", 16),
        ("fruits.Joy", "fruits_joy", 16),
        ("fruits.peace", "fruits_peace", 32),
        ("fruits.Peace", "fruits_peace", 32),
        ("commandments.love", "commandments_love", 64),
        ("commandments.Love", "commandments_love", 64),
    ],
)
@pytest.mark.usefixtures("setup_teardown_all_models_schemas", "mock_open")
def test_loadlines(model_label, key, expected_count, all_concrete_models, stringIO):
    """
    Assert that `loadlines` populates the correct model with
    the appropriate JSON Lines fixture.
    """
    model = all_concrete_models[key]
    assert model._default_manager.count() == 0

    call_command("loadlines", model_label, stdout=stringIO)
    assert model._default_manager.count() == expected_count
    assert (
        stringIO.getvalue().strip()
        == f"Created: {expected_count} objects of the model {model._meta.label}"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "model_label, key",
    [
        ("fruits.fixtureless", "fruits_fixtureless"),
        ("fruits.Fixtureless", "fruits_fixtureless"),
    ],
)
@pytest.mark.usefixtures("setup_teardown_all_models_schemas", "mock_open")
def test_loadlines_for_fixtureless_models(
    model_label, key, all_concrete_models, stringIO
):
    """
    Assert that `loadlines` throws appropriate command error
    when an attempt is made to use it to populate model without
    corresponding JSON Lines fixture file.
    """
    model = all_concrete_models[key]
    assert model._default_manager.count() == 0

    with pytest.raises(CommandError) as e:
        call_command("loadlines", model_label, stdout=stringIO)

    assert "Fixture file not found" in str(e.value)
    assert model._default_manager.count() == 0


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("setup_teardown_all_models_schemas", "mock_open")
def test_loadlines_for_fixtures_with_few_bad_lines(
    commandments_respect, stringIO, commandments_fixtures_dir
):
    """
    Assert that `loadlines` is lenient on bad JSON Lines,
    and prints rich information about the bad lines to stdout.

    The fixture file in this test has 8 lines, 2 of which
    aren't valid payload for the model in question.
    """
    model = commandments_respect
    model_label = "commandments.Respect"
    assert model._default_manager.count() == 0

    call_command("loadlines", model_label, stdout=stringIO)
    str_out = stringIO.getvalue().strip()

    # six out of eight objects created
    assert model._default_manager.count() == 6

    # check rich info is printed
    assert (
        "Bad payload in fixture file at "
        f"{pathlib.Path(commandments_fixtures_dir).joinpath('respect.jsonl')}:"
        "\n---- Line no.: 5"
        '\n---- Content : {"id":5, "bad_key":"bad_value"}' in str_out
    )

    assert (
        "Bad payload in fixture file at "
        f"{pathlib.Path(commandments_fixtures_dir).joinpath('respect.jsonl')}:"
        "\n---- Line no.: 7"
        '\n---- Content : {"id":7, "another_bad_key":"another_bad_value"}' in str_out
    )

    assert (
        f"Created: 6 objects of the model {model._meta.label}"
        "\nEncountered 2 bad lines in the fixture file."
        "\nPlease find rich info about the bad lines in the trace above." in str_out
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("setup_teardown_all_models_schemas", "mock_open")
def test_loadlines_for_already_populated_model(fruits_love, stringIO):
    """
    Assert that `loadlines` wipes the table for the model clean before loading lines.
    """
    model = fruits_love
    model_label = "fruits.Love"

    call_command("loadlines", model_label, stdout=copy.deepcopy(stringIO))
    assert model._default_manager.count() == 8

    call_command("loadlines", model_label, stdout=stringIO)
    assert model._default_manager.count() == 8

    str_out = stringIO.getvalue().strip()

    # ordinarily, all the lines should be Bad/Duplicate payload
    # as their corresponding objects are already present in the respective table
    # but `loadlines` should start with clean tables, so ...
    assert "Bad payload" not in str_out
    assert (
        "Clearing the database of fruits.Love objects.\n8 objects deleted.\n" in str_out
    )
