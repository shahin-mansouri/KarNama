from django.db import models


class Category(models.Model):
	ALLOWED_CATEGORIES = (
    (1, "کاریابی"),
    (2, "استخدام"),
    (3, "ساخت رزومه"),
    (4, "رزومه موفق"),
    (5, "مصاحبه شغلی"),
    (6, "مهارت‌های شغلی"),
    (7, "برند شخصی"))
	name = models.CharField(choices=ALLOWED_CATEGORIES, max_length=100, verbose_name='نام دسته‌بندی')
	slug = models.SlugField(max_length=100, unique=True, verbose_name='نشانی دسته‌بندی')


	class Meta:
		verbose_name = 'دسته‌بندی'
		verbose_name_plural = 'دسته‌بندی‌ها'

	def __str__(self):
		return self.name

class BlogPost(models.Model):
	title = models.CharField(max_length=180, verbose_name='عنوان مطلب')
	slug = models.SlugField(max_length=200, unique=True, verbose_name='نشانی مطلب')
	excerpt = models.TextField(max_length=300, verbose_name='خلاصه مطلب')
	content = models.TextField(verbose_name='متن مطلب')
	category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='دسته‌بندی')
	published_at = models.DateTimeField(verbose_name='تاریخ انتشار')
	is_published = models.BooleanField(default=False, verbose_name='منتشر شده')

	class Meta:
		ordering = ('-published_at',)
		verbose_name = 'مطلب وبلاگ'
		verbose_name_plural = 'مطالب وبلاگ'

	def __str__(self):
		return self.title


