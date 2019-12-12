import json
import pathlib

from django.apps.registry import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "model_label",
            type=str,
            help=(
                "The label of the model to be populated with the fixture.\n"
                "In the form <app_label>.<model_name>"
            ),
        )

    def handle(self, *args, **kwargs):
        app_label, model_name = kwargs["model_label"].lower().rsplit(".")

        try:
            model = apps.get_model(app_label, model_name)
        except LookupError as e:
            raise CommandError(str(e))

        fixture_filepath = pathlib.Path(settings.BASE_DIR).joinpath(
            app_label, "fixtures", f"{model._meta.verbose_name_plural}.jsonl"
        )

        try:
            with transaction.atomic():
                population = model._default_manager.count()
                if population > 0:
                    model._default_manager.all().delete()
                    self.stdout.write(
                        f"Clearing the database of {model._meta.label} objects."
                        f"\n{population} objects deleted.\n"
                    )
                self.loadlines(model, fixture_filepath)
        except FileNotFoundError as e:
            raise CommandError(str(e))
        except Exception as e:
            raise CommandError(
                "\n\nTransaction was not committed due to the following exception:"
                f"\n{e}"
            )

    def loadlines(self, model, fixture_filepath):
        num_badlines = 0

        for count, line in enumerate(self.iter_fixture_file_lines(fixture_filepath)):
            try:
                payload = json.loads(line)
                model._default_manager.create(**payload)
            except Exception:
                num_badlines += 1
                self.stdout.write(
                    f"Bad payload in fixture file at {fixture_filepath}:\n"
                    f"---- Line no.: {count + 1}\n"
                    f"---- Content : {line}\n\n"
                )

        self.stdout.write(
            f"Created: {count - num_badlines + 1} objects of "
            f"the model {model._meta.label}"
        )

        if num_badlines > 0:
            self.stdout.write(
                f"Encountered {num_badlines} bad lines in the fixture file.\n"
                "Please find rich info about the bad lines in the trace above."
            )

    def iter_fixture_file_lines(self, fixture_filepath):
        try:
            with open(fixture_filepath, mode="rt") as f:
                for line in f:
                    yield line
        except FileNotFoundError:
            raise FileNotFoundError(
                "Fixture file not found.\n"
                "Please make sure the appropriate fixture exists "
                f"in a file at {fixture_filepath}"
            )
