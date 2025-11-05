import os

from django.contrib.auth.models import AbstractUser, User
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=100, verbose_name='ФИО')
    email = models.EmailField(unique=True, verbose_name='Email')

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

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category-detail', kwargs={'pk': self.pk})

from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',) # Отображать имя категории в списке админки

    class Meta:
        ordering = ['-created_at']

    # class Comment(models.Model):
    #     title = models.CharField(max_length=255, verbose_name='Заголовок')
    #     post = models.ForeignKey('DesignRequest', on_delete=models.CASCADE, null=True, verbose_name='Пост')
    #     description = models.TextField(verbose_name='Описание')
    #     comment_image = models.ImageField(upload_to='create_request/', null=True, blank=True, verbose_name='Изображение')
    #
    #     def __str__(self):
    #         return self.title
    #
    #     class Meta:
    #         verbose_name = 'Комментарий'
    #         verbose_name_plural = 'Комментарии'