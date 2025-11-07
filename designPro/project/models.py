from django.contrib.auth.models import AbstractUser, User
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.db import models

class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=100, verbose_name='ФИО')
    email = models.EmailField(unique=True, verbose_name='Email')

    # Добавь related_name чтобы избежать конфликтов
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='customuser_set',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',
        related_query_name='user',
    )

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название категории')

    def __str__(self):
        return self.name


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
    customer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Заказчик', null=True, blank=True)
    image = models.ImageField(upload_to='design_requests/',verbose_name='Изображение', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null = True, blank = True)
    admin_comment = models.TextField(verbose_name='Комментарий администратора', null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category-detail', kwargs={'pk': self.pk})

    def can_be_deleted(self):
        """Проверка, можно ли удалить заявку"""
        return self.status == 'new'

    def can_change_status(self, new_status):
        """Проверка возможности смены статуса"""
        if self.status != 'new':
            return False

        if new_status == 'complete':
            return bool(self.image)
        elif new_status == 'in-progress':
            return bool(self.admin_comment)

        return False

from django.contrib import admin
from .models import Category

# Зарегистрируйте модель Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',) # Отображать имя категории в списке админки

    class Meta:
        ordering = ['-created_at']

