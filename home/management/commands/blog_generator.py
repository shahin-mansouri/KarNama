import json
import random
import dashscope
from django.utils.text import slugify
from django.utils import timezone
from home.models import BlogPost, Category
from django.core.management.base import BaseCommand
from django.conf import settings

dashscope.base_http_api_url = "https://dashscope-intl.aliyuncs.com/api/v1"


class Command(BaseCommand):
    help = "Generate a blog post using Qwen"

    def handle(self, *args, **options):
        blog = blog_generator()
        blog_json = json.loads(blog)
        category_name = blog_json["category"]
        category, _ = Category.objects.get_or_create(
            name=category_name,
            defaults={"slug": slugify(category_name, allow_unicode=True)},
        )

        BlogPost.objects.create(
            title=blog_json["title"],
            slug=slugify(blog_json["title"], allow_unicode=True),
            excerpt=blog_json["excerpt"],
            content=blog_json["content"],
            category=category,
            published_at=timezone.now(),
            is_published=True,
        )
        self.stdout.write("Blog generated successfully.")



ALLOWED_CATEGORIES = (
    "کاریابی",
    "استخدام",
    "ساخت رزومه",
    "رزومه موفق",
    "مصاحبه شغلی",
    "مهارت‌های شغلی",
    "برند شخصی",
)

def blog_generator():
    # image_path = os.path.abspath(f"./downloads/{image}")
    text=build_prompt(categorie=random.choice(ALLOWED_CATEGORIES))
    messages = [
    {
        "role": "user",
        "content": [
            {"text": text}]
    }]
    response = dashscope.MultiModalConversation.call(
        api_key=settings.DASHSCOPE_API_KEY,
        model=settings.DASHSCOPE_MODEL,
        messages=messages
    )
    return response.output.choices[0].message.content[0]["text"]


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


