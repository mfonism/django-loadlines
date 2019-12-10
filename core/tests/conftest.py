from io import StringIO

from django.apps.registry import apps
from django.conf import settings
from django.db import connection, models
from django.db.models.base import ModelBase

import pytest


def get_or_create_concrete_model(model):
    """
    Returns the concrete version of argument model.

    Argument model may be a concrete model, in which case, it is returned as is.
    Otherwise a concrete model programmatically created from argument model is returned.
    """
    try:
        return apps.get_model(model._meta.label_lower)
    except LookupError:
        return ModelBase(model.__name__, (model,), {"__module__": model.__module__})


@pytest.fixture(name="fruits_love", scope="module")
def fixture_concrete_fruits_love_model():
    """
    Returns a concrete `Love` model in a `fruits` app.
    """

    class Love(models.Model):
        class Meta:
            abstract = True
            app_label = "fruits"

    return get_or_create_concrete_model(Love)


@pytest.fixture(name="fruits_joy", scope="module")
def fixture_concrete_fruits_joy_model():
    """
    Returns a concrete `Joy` model in a `fruits` app.
    """

    class Joy(models.Model):
        class Meta:
            abstract = True
            app_label = "fruits"

    return get_or_create_concrete_model(Joy)


@pytest.fixture(name="fruits_peace", scope="module")
def fixture_concrete_fruits_peace_model():
    """
    Returns a concrete `Peace` model in a `fruits` app.
    """

    class Peace(models.Model):
        class Meta:
            abstract = True
            app_label = "fruits"

    return get_or_create_concrete_model(Peace)


@pytest.fixture(name="fruits_fixtureless", scope="module")
def fixture_concrete_fruits_fixtureless_model():
    """
    Returns a concrete `Fixtureless` model in a `fruits` app.

    The model `Fixtureless` is so-called because it mocks a model
    which has no corresponding line JSON Lines fixtures file.
    """

    class Fixtureless(models.Model):
        class Meta:
            abstract = True
            app_label = "fruits"

    return get_or_create_concrete_model(Fixtureless)


@pytest.fixture(name="all_concrete_fruits_models", scope="module")
def fixture_all_concrete_fruits_models(
    fruits_love, fruits_joy, fruits_peace, fruits_fixtureless
):
    """
    Returns a map of all concrete models in the `fruits` app.
    """
    return {
        "fruits_love": fruits_love,
        "fruits_joy": fruits_joy,
        "fruits_peace": fruits_peace,
        "fruits_fixtureless": fruits_fixtureless,
    }


@pytest.fixture(name="setup_teardown_fruits_models_schemas")
def fixture_setup_teardown_fruits_models_schema(all_concrete_fruits_models):
    """
    Ensures setup and teardown for schema of the concrete fruits models.
    """
    with connection.schema_editor() as schema_editor:
        # setup all schemas
        for model in all_concrete_fruits_models.values():
            schema_editor.create_model(model)
        # yield control to code which makes use of any of the schema
        yield
        # finally, teardown all schemas
        for model in all_concrete_fruits_models.values():
            schema_editor.delete_model(model)


@pytest.fixture(name="fruits_fixtures_dir")
def fixture_fruits_fixtures_dir():
    return settings.BASE_DIR.joinpath("fruits", "fixtures")


@pytest.fixture
def mock_open(monkeypatch, fruits_fixtures_dir):
    """
    Monkeypatch `open` to yield the json lines of the appropriate file.
    """
    import builtins
    from contextlib import contextmanager

    # why the contextmanager decorator?
    # because `open` is used in a `with` statement in the code that's to be tested

    @contextmanager
    def imposter(filepath, *args, **kwargs):
        if filepath.parent == fruits_fixtures_dir:
            if filepath.stem == "love":
                yield ((f'{{"id":{i}}}') for i in range(1, 9))
            elif filepath.stem == "joy":
                yield ((f'{{"id":{i}}}') for i in range(1, 17))
            elif filepath.stem == "peace":
                yield ((f'{{"id":{i}}}') for i in range(1, 33))
            else:
                raise FileNotFoundError
        else:
            raise FileNotFoundError

    monkeypatch.setattr(builtins, "open", imposter)


@pytest.fixture(name="stringIO")
def fixture_stringIO():
    return StringIO()
