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
        self.atomically_loadlines(model, fixture_filepath)

    def atomically_loadlines(self, model, fixture_filepath):
        try:
            with transaction.atomic():
                self.wipe_table(model)
                self.loadlines(model, fixture_filepath)
        except FileNotFoundError as e:
            raise CommandError(str(e))
        except Exception as e:
            raise CommandError(
                "\n\nTransaction was not committed due to the following exception:"
                f"\n{e}"
            )

    def wipe_table(self, model):
        count = model._default_manager.count()
        if count > 0:
            model._default_manager.all().delete()
            self.report_wipe_table(model._meta.label, count)

    def loadlines(self, model, fixture_filepath):
        num_badlines = 0

        for line_no, line in enumerate(
            self.iter_fixture_file_lines(fixture_filepath), 1
        ):
            try:
                payload = json.loads(line)
                model._default_manager.create(**payload)
            except Exception:
                num_badlines += 1
                self.report_bad_payload(fixture_filepath, line_no, content=line)

        self.report_loadlines(
            model_label=model._meta.label,
            num_loaded=line_no - num_badlines,
            num_skipped=num_badlines,
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

    def report_wipe_table(self, model_label, num_rows_wiped):
        self.stdout.write(
            f"Clearing the database of {model_label} objects."
            f"\n{num_rows_wiped} objects deleted.\n"
        )

    def report_bad_payload(self, fixture_filepath, line_no, content):
        self.stdout.write(
            f"Bad payload in fixture file at {fixture_filepath}:\n"
            f"---- Line no.: {line_no}\n"
            f"---- Content : {content}\n\n"
        )

    def report_loadlines(self, model_label, num_loaded, num_skipped):
        self.stdout.write(f"Created: {num_loaded} objects of the model {model_label}")

        if num_skipped > 0:
            self.stdout.write(
                f"Encountered {num_skipped} bad lines in the fixture file.\n"
                "Please find rich info about the bad lines in the trace above."
            )
