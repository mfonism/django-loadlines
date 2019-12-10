import pathlib

BASE_DIR = pathlib.Path(__file__).absolute().parent.parent

SECRET_KEY = "5jf7o$aomj_*+2wl-+po7*d(zs4nf_jf2r8sgvf_4x2rp3v#0_"

INSTALLED_APPS = [
    "core.apps.CoreConfig",
    "core.tests.utils.FruitsConfig",
    "core.tests.utils.CommandmentsConfig",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_DIR.joinpath("db.sqlite3")),
    }
}
