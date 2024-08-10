from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User, AbstractUser
import random
import string
from datetime import timedelta
from django.utils import timezone

from e_commerce import settings


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    registration_method = models.CharField(max_length=20, blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )


class AllProducts(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    main_img = models.ImageField(upload_to='uploads/', blank=True, null=True)
    img_1 = models.ImageField(upload_to='uploads/', blank=True, null=True)
    img_2 = models.ImageField(upload_to='uploads/', blank=True, null=True)
    img_3 = models.ImageField(upload_to='uploads/', blank=True, null=True)
    img_4 = models.ImageField(upload_to='uploads/', blank=True, null=True)
    img_5 = models.ImageField(upload_to='uploads/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField(default=0)
    category = models.ForeignKey('Category', on_delete=models.PROTECT, related_name='category')
    slug = models.SlugField(unique=True, null=True)

    class Meta:
        verbose_name = 'AllProduct'
        verbose_name_plural = 'AllProduct'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product-detail', args=[str(self.id)])


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class VerificationCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    code = models.CharField(max_length=6, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join(random.choices(string.digits, k=6))
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)
