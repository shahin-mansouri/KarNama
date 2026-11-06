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



import re

def _validate_blog_data(blog_json, expected_category):

    if not isinstance(blog_json, dict):
        raise ValueError("Model response must be a JSON object.")

    # فیلدهای موردنیاز مدل BlogPost
    required_fields = (
        "title",
        "slug",
        "excerpt",
        "content",
        "category",
    )

    # بررسی وجود و معتبر بودن فیلدها
    for field in required_fields:
        value = blog_json.get(field)

        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"Model response contains an invalid or empty '{field}' field."
            )

    # بررسی دسته‌بندی
    if blog_json["category"] != expected_category:
        blog_json["category"] = expected_category
        pass
        # raise ValueError(
        #     "Model response category does not match the requested category."
        # )

    # بررسی محدودیت طول عنوان
    if len(blog_json["title"]) > 180:
        raise ValueError("Generated article title exceeds 180 characters.")

    # بررسی محدودیت طول خلاصه
    if len(blog_json["excerpt"]) > 300:
        raise ValueError("Generated article excerpt exceeds 300 characters.")

    # بررسی محدودیت طول اسلاگ
    if len(blog_json["slug"]) > 200:
        raise ValueError("Generated article slug exceeds 200 characters.")

    # بررسی فرمت اسلاگ
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", blog_json["slug"]):
        raise ValueError("Generated article slug has an invalid format.")

    # بررسی محتوای HTML
    if not re.search(r"<(h2|h3|p|ul|ol|blockquote)\b", blog_json["content"]):
        raise ValueError("Generated article content does not contain valid HTML structure.")

    return blog_json



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
            lambda: _validate_blog_data(
                _parse_model_response(response), expected_category=category
            ),
            remaining_after_seconds=4,
        )

    return _validate_blog_data(
        _parse_model_response(request()), expected_category=category
    )



def build_prompt(categorie):
    return f"""
به‌عنوان یک متخصص ارشد SEO، استراتژیست محتوا و نویسنده حرفه‌ای
در حوزه کاریابی، استخدام، ساخت رزومه و توسعه شغلی فعالیت کن.

وظیفه تو تولید یک مقاله فارسی حرفه‌ای، اختصاصی، کاربردی و
بهینه‌شده برای موتورهای جستجو درباره دسته‌بندی «{categorie}» است.

هدف، تولید محتوایی است که علاوه بر داشتن پتانسیل کسب جایگاه مناسب
در نتایج گوگل، واقعاً به مخاطبان سایت کمک کند و ارزش مطالعه داشته باشد.

### ۱. انتخاب موضوع مقاله
- موضوعی مشخص، جذاب و متناسب با دسته‌بندی انتخاب کن.
- موضوع باید یکی از نیازها، چالش‌ها یا سؤالات واقعی کارجویان و متخصصان را هدف قرار دهد.
- از انتخاب موضوعات بیش از حد عمومی، تکراری و کلیشه‌ای خودداری کن.
- مقاله باید زاویه دید مشخص و ارزش افزوده داشته باشد.
- از بازنویسی سطحی مقالات رایج اینترنت خودداری کن.

### ۲. استانداردهای نگارش
- لحن رسمی، روان، حرفه‌ای و قابل فهم باشد.
- مخاطبان شامل کارجویان، کارمندان، متخصصان، مدیران و کارفرمایان هستند.
- مطالب دقیق، کاربردی، قابل اجرا و متناسب با نیاز مخاطب باشند.
- از مثال‌های واقع‌گرایانه و سناریوهای کاربردی استفاده کن.
- مراحل اجرایی، راهکارها، نکات تخصصی و اشتباهات رایج را در صورت تناسب توضیح بده.
- از مقدمه‌های طولانی، جملات انگیزشی بی‌محتوا و تکرار مطالب خودداری کن.
- هیچ آمار، پژوهش، نقل‌قول یا ادعای تخصصی ساختگی ارائه نکن.

### ۳. اصول SEO
- عنوان مقاله جذاب، دقیق و دارای کلمه کلیدی اصلی باشد.
- کلمه کلیدی اصلی را طبیعی در عنوان، مقدمه و بخش‌های مرتبط استفاده کن.
- از کلمات کلیدی مرتبط و عبارات هم‌معنی به شکل طبیعی استفاده کن.
- ساختار محتوا با هدف جستجوی کاربر (Search Intent) مطابقت داشته باشد.
- تیترها توصیفی، جذاب و دارای ساختار سلسله‌مراتبی باشند.
- از Keyword Stuffing خودداری کن.
- محتوا باید جامع و پاسخگوی سؤال اصلی مخاطب باشد.
- مقاله را صرفاً برای افزایش تعداد کلمات طولانی نکن.

### ۴. ساختار مقاله
محتوا باید متناسب با موضوع شامل موارد زیر باشد:
- مقدمه کوتاه و هدفمند.
- بخش‌های اصلی با تیترهای H2.
- زیربخش‌های تکمیلی با تیترهای H3.
- توضیحات تخصصی و کاربردی.
- مثال‌ها و راهکارهای اجرایی.
- اشتباهات رایج و روش جلوگیری از آن‌ها.
- جمع‌بندی و نتیجه‌گیری کاربردی.
- در صورت تناسب، ۳ تا ۵ سؤال متداول همراه با پاسخ.

از ایجاد تیترهای غیرضروری یا تکراری خودداری کن.

### ۵. استاندارد HTML
مقدار content باید یک رشته HTML معتبر و آماده ذخیره در Django باشد.

فقط از تگ‌های زیر استفاده کن:
h2, h3, p, ul, ol, li, strong, blockquote

قوانین:
- از h1 استفاده نکن؛ عنوان اصلی در فیلد title ذخیره می‌شود.
- از Markdown استفاده نکن.
- هیچ CSS یا JavaScript تولید نکن.
- از تگ‌های html، head و body استفاده نکن.
- ساختار HTML مرتب، معنایی و استاندارد باشد.
- پاراگراف‌ها کوتاه و خوانا باشند.

### ۶. استاندارد فیلدهای خروجی

title:
عنوان اصلی مقاله با حداکثر ۱۸۰ کاراکتر.
عنوان باید جذاب، طبیعی و مناسب SEO باشد.

slug:
یک نشانی انگلیسی، کوتاه، خوانا و مرتبط با موضوع مقاله تولید کن.
فقط از حروف کوچک انگلیسی، اعداد و خط تیره استفاده کن.
فاصله، حروف فارسی و کاراکترهای غیرمجاز نداشته باشد.

excerpt:
خلاصه‌ای جذاب، حرفه‌ای و کاربردی با حداکثر ۳۰۰ کاراکتر.
خلاصه باید موضوع مقاله و مهم‌ترین فایده مطالعه آن را منتقل کند.

content:
متن کامل مقاله به‌صورت HTML معتبر و ساختاریافته.
محتوا باید جامع، غیرتکراری و آماده انتشار باشد.

category:
مقدار این فیلد باید دقیقاً برابر با دسته‌بندی ورودی باشد:
{categorie}

### ۷. قوانین الزامی خروجی JSON

فقط یک JSON معتبر برگردان.
هیچ توضیحی قبل یا بعد از JSON ننویس.
از Markdown و Code Block استفاده نکن.

ساختار خروجی دقیقاً باید به شکل زیر باشد:

{{
    "title": "عنوان مقاله",
    "slug": "english-article-slug",
    "excerpt": "خلاصه مقاله",
    "content": "<h2>عنوان بخش</h2><p>متن مقاله</p>",
    "category": "{categorie}"
}}

قوانین نهایی:
- دقیقاً همین ۵ کلید را تولید کن.
- هیچ کلید اضافی تولید نکن.
- فیلدهای published_at و is_published را تولید نکن.
- مقدار category باید دقیقاً برابر با «{categorie}» باشد.
- تمام رشته‌ها باید با Double Quote محصور شوند.
- کاراکترهای نقل‌قول داخل رشته‌ها باید Escape شوند.
- خروجی باید مستقیماً با json.loads در Python قابل پردازش باشد.
- محتوای HTML باید داخل رشته content قرار بگیرد.
- هیچ توضیح یا محتوای اضافی خارج از JSON تولید نکن.
""".strip()
