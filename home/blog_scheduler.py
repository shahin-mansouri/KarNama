import threading

from django.db import close_old_connections


PUBLISH_INTERVAL_SECONDS = 5 * 60 * 60
_scheduler_started = False
_scheduler_lock = threading.Lock()
_stop_event = threading.Event()


def _publish_periodically():
    while True:
        if not _stop_event.wait(PUBLISH_INTERVAL_SECONDS):
            close_old_connections()
            try:
                from home.management.commands.blog_generator import publish_generated_blog

                publish_generated_blog()
            except Exception:
                pass
            finally:
                close_old_connections()


def start_blog_scheduler():
    global _scheduler_started
    with _scheduler_lock:
        if _scheduler_started:
            return
        _scheduler_started = True

    threading.Thread(
        target=_publish_periodically,
        name="blog-auto-publisher",
        daemon=True,
    ).start()
