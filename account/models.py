from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone

import secrets
from datetime import timedelta


class UserCustom(AbstractUser):
    phone_number = models.CharField(max_length=11, unique=True, verbose_name='شماره تلفن')
    address = models.TextField(blank=True, null=True, verbose_name='آدرس')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone_number', 'first_name', 'last_name']


    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'


class OTPCode(models.Model):
    phone_number = models.CharField(max_length=11, db_index=True, verbose_name='شماره تلفن')
    code_hash = models.CharField(max_length=128, verbose_name='کد رمزنگاری‌شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ایجاد')
    expires_at = models.DateTimeField(verbose_name='زمان انقضا')
    attempts = models.PositiveSmallIntegerField(default=0, verbose_name='تعداد تلاش')
    used_at = models.DateTimeField(null=True, blank=True, verbose_name='زمان مصرف')
    session_key = models.CharField(max_length=40, blank=True, verbose_name='شناسه session')

    MAX_ATTEMPTS = 5

    @classmethod
    def issue(cls, phone_number, session_key=''):
        code = f'{secrets.randbelow(1000000):06d}'
        otp = cls.objects.create(
            phone_number=phone_number,
            code_hash=make_password(code),
            expires_at=timezone.now() + timedelta(minutes=5),
            session_key=session_key or '',
        )
        return otp, code

    def verify(self, code, session_key=''):
        if self.used_at or timezone.now() >= self.expires_at:
            return False
        if self.session_key and self.session_key != session_key:
            return False
        if self.attempts >= self.MAX_ATTEMPTS:
            return False

        self.attempts += 1
        valid = check_password(code, self.code_hash)
        if valid:
            self.used_at = timezone.now()
            self.save(update_fields=('attempts', 'used_at'))
        else:
            self.save(update_fields=('attempts',))
        return valid

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'کد یکبارمصرف'
        verbose_name_plural = 'کدهای یکبارمصرف'


class UserProfile(models.Model):

    MARITAL_STATUS_CHOICES = (
        ('single', 'مجرد'),
        ('married', 'متاهل'),
    )
    MILITARY_STATUS_CHOICES = (
        ('completed', 'پایان خدمت'),
        ('exempt', 'معاف'),
        ('in_progress', 'در حال انجام'),
        ('not_applicable', 'مشمول نمی‌شود'),
    )

    user = models.OneToOneField(UserCustom, on_delete=models.CASCADE, verbose_name='کاربر')
    title = models.CharField(max_length=20, verbose_name='عنوان شغلی')
    bio = models.TextField(blank=True, null=True, verbose_name='معرفی')
    profile_picture = models.ImageField(upload_to='media/profile_pictures/', blank=True, null=True, verbose_name='تصویر پروفایل')
    address = models.TextField(blank=True, null=True, verbose_name='آدرس')
    birth_date = models.DateField(blank=True, null=True, verbose_name='تاریخ تولد')
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True, verbose_name='وضعیت تاهل')
    military_status = models.CharField(max_length=20, choices=MILITARY_STATUS_CHOICES, blank=True, verbose_name='وضعیت سربازی')

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = 'پروفایل کاربر'
        verbose_name_plural = 'پروفایل‌های کاربران'

class AboutMe(models.Model):
    user = models.OneToOneField(UserCustom, on_delete=models.CASCADE, verbose_name='کاربر')
    about_me = models.TextField(blank=True, null=True, verbose_name='درباره من')

    def __str__(self):
        return f"{self.user.username}'s About Me"

    class Meta:
        verbose_name = 'درباره من'
        verbose_name_plural = 'درباره من'


class Skill(models.Model):
    user = models.ForeignKey(UserCustom, on_delete=models.CASCADE, verbose_name='کاربر')
    name = models.CharField(max_length=50, verbose_name='نام مهارت')
    proficiency = models.IntegerField(verbose_name='درصد تسلط')

    def __str__(self):
        return f"{self.name} - {self.proficiency}%"

    class Meta:
        verbose_name = 'مهارت'
        verbose_name_plural = 'مهارت‌ها'


class WorkExperience(models.Model):
    user = models.ForeignKey(UserCustom, on_delete=models.CASCADE, verbose_name='کاربر')
    position = models.CharField(max_length=100, verbose_name='سمت شغلی')
    company_name = models.CharField(max_length=100, verbose_name='نام شرکت')
    address = models.TextField(blank=True, null=True, verbose_name='آدرس شرکت')
    start_date = models.DateField(verbose_name='تاریخ شروع')
    end_date = models.DateField(blank=True, null=True, verbose_name='تاریخ پایان')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')

    def __str__(self):
        return f"{self.position} at {self.company_name}"

    class Meta:
        verbose_name = 'تجربه کاری'
        verbose_name_plural = 'تجربه‌های کاری'

class WorkTechUse(models.Model):
    work_experience = models.ForeignKey(WorkExperience, on_delete=models.CASCADE, verbose_name='تجربه کاری')
    technology = models.CharField(max_length=50, verbose_name='فناوری')

    class Meta:
        verbose_name = 'فناوری استفاده‌شده'
        verbose_name_plural = 'فناوری‌های استفاده‌شده'


class FieldOfActivity(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام حوزه')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'حوزه فعالیت'
        verbose_name_plural = 'حوزه‌های فعالیت'

class Project(models.Model):
    field_of_activity = models.ForeignKey(FieldOfActivity, on_delete=models.CASCADE, verbose_name='حوزه فعالیت')
    user = models.ForeignKey(UserCustom, on_delete=models.CASCADE, verbose_name='کاربر')
    name = models.CharField(max_length=100, verbose_name='نام پروژه')
    technologies_used = models.CharField(max_length=200, verbose_name='فناوری‌های استفاده‌شده')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    github_link = models.URLField(blank=True, null=True, verbose_name='لینک گیت‌هاب')
    demo_link = models.URLField(blank=True, null=True, verbose_name='لینک نسخه نمایشی')
    project_picture = models.ImageField(upload_to='projects/', blank=True, null=True, verbose_name='تصویر پروژه')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'پروژه'
        verbose_name_plural = 'پروژه‌ها'


class Certificate(models.Model):
    user = models.ForeignKey(UserCustom, on_delete=models.CASCADE, verbose_name='کاربر')
    name = models.CharField(max_length=150, verbose_name='نام گواهینامه')
    issuer = models.CharField(max_length=100, verbose_name='صادرکننده')
    issue_date = models.DateField(blank=True, null=True, verbose_name='تاریخ دریافت')
    certificate_link = models.URLField(blank=True, null=True, verbose_name='لینک گواهینامه')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'گواهینامه'
        verbose_name_plural = 'گواهینامه‌ها'


class Language(models.Model):
    user = models.ForeignKey(UserCustom, on_delete=models.CASCADE, verbose_name='کاربر')
    name = models.CharField(max_length=80, verbose_name='نام زبان')
    proficiency = models.IntegerField(verbose_name='درصد تسلط')

    def __str__(self):
        return f'{self.name} - {self.proficiency}%'

    class Meta:
        verbose_name = 'زبان'
        verbose_name_plural = 'زبان‌ها'


class Research(models.Model):
    user = models.ForeignKey(UserCustom, on_delete=models.CASCADE, verbose_name='کاربر')
    title = models.CharField(max_length=200, verbose_name='عنوان تحقیق')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات تحقیق')
    year = models.PositiveIntegerField(verbose_name='سال تحقیق')
    link = models.URLField(blank=True, null=True, verbose_name='لینک تحقیق')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'تحقیق'
        verbose_name_plural = 'تحقیقات'
        ordering = ('-year', '-id')


class SocialLink(models.Model):
    PLATFORM_CHOICES = (
        ('github', 'GitHub'),
        ('linkedin', 'LinkedIn'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter / X'),
        ('telegram', 'Telegram'),
        ('facebook', 'Facebook'),
        ('youtube', 'YouTube'),
        ('website', 'وب‌سایت'),
    )

    user = models.ForeignKey(UserCustom, on_delete=models.CASCADE, verbose_name='کاربر')
    platform = models.CharField(max_length=30, choices=PLATFORM_CHOICES, verbose_name='شبکه اجتماعی')
    url = models.URLField(verbose_name='لینک')

    def __str__(self):
        return f'{self.get_platform_display()} - {self.user.username}'

    class Meta:
        verbose_name = 'شبکه اجتماعی'
        verbose_name_plural = 'شبکه‌های اجتماعی'


