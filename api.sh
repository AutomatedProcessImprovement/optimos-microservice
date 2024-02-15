#!/bin/sh -ex
gunicorn --workers=3 --threads=3 -b :5000 app:app --timeout 1000
