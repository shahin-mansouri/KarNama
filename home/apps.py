import os
import sys

from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'

    def ready(self):
        if not _is_web_server_process():
            return

        from .blog_scheduler import start_blog_scheduler

        start_blog_scheduler()


def _is_web_server_process():
    if "blog_generator" in sys.argv:
        return False

    command = os.path.basename(sys.argv[0]).lower()
    if command in {"gunicorn", "uvicorn", "daphne", "uwsgi"}:
        return True

    if "runserver" in sys.argv:
        return (
            os.environ.get("RUN_MAIN", "").lower() == "true"
            or "--noreload" in sys.argv
        )

    return False
