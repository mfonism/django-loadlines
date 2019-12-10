from django.db import connection, models
from django.db.models.base import ModelBase

import pytest


@pytest.fixture(name="fruits_love", scope="module")
def fixture_concrete_fruits_love_model():
    """
    Returns a concrete `Love` model in a `fruits` app.
    """

    class Love(models.Model):
        class Meta:
            abstract = True
            app_label = "fruits"

    return ModelBase(Love.__name__, (Love,), {"__module__": Love.__module__})


@pytest.fixture(name="fruits_joy", scope="module")
def fixture_concrete_fruits_joy_model():
    """
    Returns a concrete `Joy` model in a `fruits` app.
    """

    class Joy(models.Model):
        class Meta:
            abstract = True
            app_label = "fruits"

    return ModelBase(Joy.__name__, (Joy,), {"__module__": Joy.__module__})


@pytest.fixture(name="fruits_peace", scope="module")
def fixture_concrete_fruits_peace_model():
    """
    Returns a concrete `Peace` model in a `fruits` app.
    """

    class Peace(models.Model):
        class Meta:
            abstract = True
            app_label = "fruits"

    return ModelBase(Peace.__name__, (Peace,), {"__module__": Peace.__module__})


@pytest.fixture(name="all_concrete_fruits_models", scope="module")
def fixture_all_concrete_fruits_models(fruits_love, fruits_joy, fruits_peace):
    """
    Returns a map of all concrete models in the `fruits` app.
    """
    return {
        "fruits_love": fruits_love,
        "fruits_joy": fruits_joy,
        "fruits_peace": fruits_peace,
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
