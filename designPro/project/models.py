import os

from django.contrib.auth.models import AbstractUser, User
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.db import models

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    patronymic = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True, verbose_name='Email')
    agreement = models.BooleanField(default=False)
    groups = models.ManyToManyField('auth.Group', verbose_name='groups', blank=True, help_text='The groups this user belongs to.', related_name='customuser_set', related_query_name='user', )
    user_permissions = models.ManyToManyField('auth.Permission', verbose_name='user permissions',blank=True, help_text='Specific permissions for this user.',related_name='customuser_set',related_query_name='user',)

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название категории')

    def __str__(self):
        return self.name


ALLOWED_USERREQUEST_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp']

def validate_userrequest_image_extension(value):
    ext=os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_USERREQUEST_IMAGE_EXTENSIONS:
        raise ValidationError('Неккоректный формат изображения')



class DesignRequest(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in-progress', 'Принято в работу'),
        ('complete', 'Выполнено'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    title = models.CharField(max_length=100, verbose_name='Название заявки')
    description = models.TextField(verbose_name='Описание')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name='Категория')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Заказчик', null=True, blank=True)
    image = models.ImageField(upload_to='design_requests/',verbose_name='Изображение', null=True, blank=False, validators=[validate_userrequest_image_extension])
    created_at = models.DateTimeField(auto_now_add=True, null = True, blank = True)

    design_image = models.ImageField(upload_to='design_img/',blank=False, null=True, validators=[validate_userrequest_image_extension])
    admin_comment = models.TextField(null=True, blank=True)


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category-detail', kwargs={'pk': self.pk})

    def can_be_deleted(self):
        """Проверка, можно ли удалить заявку"""
        return self.status == 'new'

from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

    class Meta:
        ordering = ['-created_at']

