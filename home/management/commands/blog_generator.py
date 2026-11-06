import json
import random
import threading
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from openai import OpenAI

from home.models import BlogPost, Category


MODEL_RESPONSE_ESTIMATE_SECONDS = 60

ALLOWED_CATEGORIES = (
    "کاریابی",
    "استخدام",
    "ساخت رزومه",
    "رزومه موفق",
    "مصاحبه شغلی",
    "مهارت‌های شغلی",
    "برند شخصی",
)


class Command(BaseCommand):
    help = "Generate a blog post using Qwen"

    def handle(self, *args, **options):
        progress = _CommandProgress(self.stdout)
        blog_json = blog_generator(progress=progress)
        category = progress.run_stage(
            "مرحله ۴ از ۵: آماده‌سازی دسته‌بندی",
            2,
            lambda: _get_or_create_category(blog_json["category"]),
            remaining_after_seconds=2,
        )
        progress.run_stage(
            "مرحله ۵ از ۵: ذخیره و انتشار مقاله",
            2,
            lambda: _save_blog_post(blog_json, category),
        )
        self.stdout.write("مقاله با موفقیت منتشر شد.")


class _CommandProgress:
    def __init__(self, output):
        self.output = output

    def write_stage(self, label, remaining_seconds):
        self.output.write(
            f"{label} — زمان تقریبی تا پایان: حدود {remaining_seconds} ثانیه\n"
        )
        self.output.flush()

    def run_stage(
        self, label, estimate_seconds, operation, remaining_after_seconds=0
    ):
        stop = threading.Event()
        started_at = time.monotonic()

        def show_countdown():
            while not stop.wait(1):
                elapsed = int(time.monotonic() - started_at)
                remaining = (
                    estimate_seconds - elapsed + remaining_after_seconds
                )
                if remaining > 0:
                    status = f"حدود {remaining} ثانیه باقی‌مانده"
                else:
                    status = "بیشتر از زمان تخمینی؛ هنوز در حال انجام"
                self.output.write(f"\r{label} — {status}   ", ending="")
                self.output.flush()

        total_estimate = estimate_seconds + remaining_after_seconds
        self.output.write(f"{label} — زمان تقریبی تا پایان: حدود {total_estimate} ثانیه\n")
        self.output.flush()
        ticker = threading.Thread(target=show_countdown, daemon=True)
        ticker.start()
        try:
            result = operation()
        except Exception:
            stop.set()
            ticker.join()
            self.output.write(f"\r{label} — ناموفق\n", ending="")
            self.output.flush()
            raise

        stop.set()
        ticker.join()
        elapsed = int(time.monotonic() - started_at)
        self.output.write(
            f"\r{label} — انجام شد ({elapsed} ثانیه)   \n", ending=""
        )
        self.output.flush()
        return result


def _extract_text_from_content(content):
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                value = item.get("text") or item.get("content")
            else:
                value = getattr(item, "text", None) or getattr(item, "content", None)

            if isinstance(value, list):
                value = _extract_text_from_content(value)

            if isinstance(value, str):
                parts.append(value)

        return "".join(parts).strip()

    return ""


def _parse_model_response(response):
    payload = getattr(response, "output", None)
    text = ""

    if isinstance(payload, list):
        for item in payload:
            if hasattr(item, "content"):
                text = _extract_text_from_content(item.content)
                if text:
                    break

    if not text:
        choices = getattr(response, "choices", None) or []
        for choice in choices:
            message = getattr(choice, "message", None)
            text = _extract_text_from_content(getattr(message, "content", None))
            if text:
                break

    if not text:
        raise ValueError("Model response did not include any text content.")

    text = text.strip()
    if text.startswith("```"):
        text = text.replace("```json", "", 1).replace("```", "", 1).strip()

    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(text[start : end + 1])

    raise ValueError("Model response was not valid JSON.")


def _get_or_create_category(category_name):
    return Category.objects.get_or_create(
        name=category_name,
        defaults={"slug": slugify(category_name, allow_unicode=True)},
    )[0]


def _save_blog_post(blog_json, category):
    base_slug = (
        slugify(blog_json["title"], allow_unicode=True)[:190].rstrip("-")
        or "blog-post"
    )
    slug = base_slug
    suffix = 2
    while BlogPost.objects.filter(slug=slug).exists():
        suffix_text = f"-{suffix}"
        slug = f"{base_slug[: 200 - len(suffix_text)].rstrip('-')}{suffix_text}"
        suffix += 1

    BlogPost.objects.create(
        title=blog_json["title"],
        slug=slug,
        excerpt=blog_json["excerpt"],
        content=blog_json["content"],
        category=category,
        published_at=timezone.now(),
        is_published=True,
    )


def publish_generated_blog():
    blog_json = blog_generator()
    category = _get_or_create_category(blog_json["category"])
    _save_blog_post(blog_json, category)


def blog_generator(progress=None):
    category = random.choice(ALLOWED_CATEGORIES)
    if progress:
        progress.write_stage(
            "مرحله ۱ از ۵: آماده‌سازی درخواست مقاله",
            MODEL_RESPONSE_ESTIMATE_SECONDS + 5,
        )
    text = build_prompt(categorie=category)
    messages = [{"role": "user", "content": text}]
    client = OpenAI(
        base_url=settings.KILO_BASE_URL,
        api_key=settings.KILO_API_KEY,
        timeout=120,
    )

    request = lambda: client.chat.completions.create(
        model=settings.KILO_MODEL,
        messages=messages,
    )
    if progress:
        response = progress.run_stage(
            "مرحله ۲ از ۵: دریافت پاسخ مدل",
            MODEL_RESPONSE_ESTIMATE_SECONDS,
            request,
            remaining_after_seconds=5,
        )
        return progress.run_stage(
            "مرحله ۳ از ۵: اعتبارسنجی محتوای مقاله",
            1,
            lambda: _parse_model_response(response),
            remaining_after_seconds=4,
        )

    return _parse_model_response(request())


def build_prompt(categorie):
    return f"""
                برای یک مقاله فارسی حرفه‌ای و کاربردی درباره دسته «{categorie}» بنویس.

                مقاله باید مناسب SEO، غیرکلیشه‌ای، کاربردی و مخصوص افراد جویای کار و متخصصان باشد.
                عنوان جذاب، خلاصه حداکثر 100 کاراکتر و محتوای کامل با تیترهای مناسب داشته باشد.

                فقط JSON معتبر و بدون Markdown برگردان:

                {{
                    "title": "عنوان مقاله",
                    "excerpt": "خلاصه مقاله",
                    "content": "متن کامل مقاله",
                    "category": "{categorie}"
                }}
                """.strip()
