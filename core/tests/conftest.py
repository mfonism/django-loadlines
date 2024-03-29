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
            verbose_name_plural = "lots_of_love"

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
            verbose_name_plural = "plenty_of_peace"

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
            verbose_name_plural = "fixturelesses"

    return get_or_create_concrete_model(Fixtureless)


@pytest.fixture(name="commandments_love", scope="module")
def fixture_concrete_commandments_love_model():
    """
    Returns a concrete `Love` model in a `commandments` app.
    """

    class Love(models.Model):
        class Meta:
            abstract = True
            app_label = "commandments"
            verbose_name_plural = "lots_of_love"

    return get_or_create_concrete_model(Love)


@pytest.fixture(name="commandments_respect", scope="module")
def fixture_concrete_commandments_respect_model():
    """
    Returns a concrete `Respect` model in a `commandments` app.
    """

    class Respect(models.Model):
        class Meta:
            abstract = True
            app_label = "commandments"
            verbose_name_plural = "respect"

    return get_or_create_concrete_model(Respect)


@pytest.fixture(name="all_concrete_models", scope="module")
def fixture_all_concrete_models(
    fruits_love,
    fruits_joy,
    fruits_peace,
    fruits_fixtureless,
    commandments_love,
    commandments_respect,
):
    """
    Returns a map of all concrete models in the test project.
    """
    return {
        "fruits_love": fruits_love,
        "fruits_joy": fruits_joy,
        "fruits_peace": fruits_peace,
        "fruits_fixtureless": fruits_fixtureless,
        "commandments_love": commandments_love,
        "commandments_respect": commandments_respect,
    }


@pytest.fixture(name="setup_teardown_all_models_schemas")
def fixture_setup_teardown_all_models_schema(all_concrete_models):
    """
    Ensures setup and teardown for schema of all the concrete models.
    """
    with connection.schema_editor() as schema_editor:
        # setup all schemas
        for model in all_concrete_models.values():
            schema_editor.create_model(model)
        # yield control to code which makes use of any of the schema
        yield
        # finally, teardown all schemas
        for model in all_concrete_models.values():
            schema_editor.delete_model(model)


@pytest.fixture(name="fruits_fixtures_dir")
def fixture_fruits_fixtures_dir():
    return settings.BASE_DIR.joinpath("fruits", "fixtures")


@pytest.fixture(name="commandments_fixtures_dir")
def fixture_commandments_fixtures_dir():
    return settings.BASE_DIR.joinpath("commandments", "fixtures")


@pytest.fixture
def mock_open(monkeypatch, fruits_fixtures_dir, commandments_fixtures_dir):
    """
    Monkeypatch `open` to yield the json lines of the appropriate file.
    """
    import builtins
    from contextlib import contextmanager

    # why the contextmanager decorator?
    # because `open` is used in a `with` statement in the code that's to be tested

    # the files we're interested in
    # are named according to the verbose_name_plural of the
    # corresponding model
    # so, you're going to see things like:
    # loves, joys, plenty_of_peace...
    # try to contain your WTFs

    @contextmanager
    def imposter(filepath, *args, **kwargs):
        if filepath.parent == fruits_fixtures_dir:
            # in fruits app

            if filepath.stem == "lots_of_love":
                # for Love model
                yield ((f'{{"id":{i}}}') for i in range(1, 9))

            elif filepath.stem == "joys":
                # for Joy model
                yield ((f'{{"id":{i}}}') for i in range(1, 17))

            elif filepath.stem == "plenty_of_peace":
                # for Peace model
                yield ((f'{{"id":{i}}}') for i in range(1, 33))

            else:
                # unrecognized model
                raise FileNotFoundError

        elif filepath.parent == commandments_fixtures_dir:
            # in commandments app
            if filepath.stem == "lots_of_love":
                # for Love model
                yield ((f'{{"id":{i}}}') for i in range(1, 65))
            elif filepath.stem == "respect":
                yield (
                    iter(
                        [
                            '{"id":1}',
                            '{"id":2}',
                            '{"id":3}',
                            '{"id":4}',
                            '{"id":5, "bad_key":"bad_value"}',
                            '{"id":6}',
                            '{"id":7, "another_bad_key":"another_bad_value"}',
                            '{"id":8}',
                        ]
                    )
                )
            else:
                # unrecognized model
                raise FileNotFoundError

        else:
            # unrecognized app
            raise FileNotFoundError

    monkeypatch.setattr(builtins, "open", imposter)


@pytest.fixture(name="stringIO")
def fixture_stringIO():
    return StringIO()
