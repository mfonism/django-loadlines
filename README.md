# Django-loadlines

Django-loadlines is a reusable Django app for loading the content of
[newline-delimited JSON](http://jsonlines.org) fixture files into the database.

# Usage

Django-loadlines exposes a command `loadlines` which is useful for
discovering newline-delimited JSON fixture files in a project and loading the
contained data into the database using the correct Django model.

```bash
$ python manage.py loadlines <app_label>.<ModelName>
```

## A few caveats

The command `loadlines` looks to match each model with __one and only one__ fixture file.

It expects that:

1. The file is named according to the `verbose_name_plural` of the model.
2. The file exists in a directory named __fixtures__ which in turn exists in the
  same app as the model.

Ideally, each line in the file should constitute valid data for a unique object of the model. As of the time of writing this document, `loadlines` will raise a command error on encountering any line that runs afoul of this ideal.

However, in the nearest future, it will have been rewritten to silently ignore such lines and just log the error to stdout.

## So, what's all this about newline-delimited JSON, anyways?
Newline-delimited JSON (also known as JSON Lines) is a convenient format for storing structured data that may be processed one record at a time.

In a JSON Lines file, each line is a valid JSON object, and lines are separated by newline characters. The biggest strength of this format is in handling lots of similar nested data structures

You can find more information about the newline-delimited JSON format in [the official documentation for the JSON Lines text file format](http://jsonlines.org).
