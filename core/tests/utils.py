import sys

from django.apps import AppConfig

import core


class FruitsConfig(AppConfig):
    """
    App config for the `fruits` app used in tests.
    """

    name = "fruits"
    # -------------
    # we have to make fruits importable in order to prevent a
    # django.core.exceptions.ImproperlyConfigured
    # exception from being thrown
    # -------------
    # we're just making it point to the `core` module for now
    sys.modules["fruits"] = core


class CommandmentsConfig(AppConfig):
    """
    App config for the `commandments` app used in tests.
    """

    name = "commandments"
    sys.modules["commandments"] = core
