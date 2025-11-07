from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
import re
from .models import  DesignRequest, Category, CustomUser

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=100,
        label='ФИО',
    )
    email = forms.EmailField(
        label='Email',
    )
    username = forms.CharField(
        label='Логин',
    )
    agreement = forms.BooleanField(
        required=True,
        label='Согласие на обработку персональных данных',
    )

    class Meta:
        model = CustomUser
        fields = ('full_name', 'username', 'email', 'password1', 'password2', 'agreement')

def file_size(value):
    limit = 2 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('Размер файла не должен превышать 2Мб.')

class DesignRequestForm(forms.ModelForm):
    Category = forms.ModelChoiceField(queryset=Category.objects.all(), label='Категория')
    create_image = forms.FileField(
    validators=[file_size, FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'bmp'])],
    label='Изображение')

    def clean_full_name(self):
        full_name = self.cleaned_data['full_name']
        if not re.match(r'^[а-яА-ЯёЁ\s\-]+$', full_name):
            raise ValidationError('ФИО должно содержать только кириллические буквы, пробелы и дефис')
        return full_name

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^[a-zA-Z\-]+$', username):
            raise ValidationError('Логин должен содержать только латинские буквы и дефис')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким логином уже существует')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='Логин',
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput()
    )

class DesignRequestForm(forms.ModelForm):
    class Meta:
        model = DesignRequest
        fields = ['title', 'description', 'category', 'image']
        labels = {'image': 'Фото помещения или план'}

class ChangeStatusForm:
    """
   #     Форма для изменения статуса заявки администратором.
   #     """
    class Meta:
        model = DesignRequest
        fields = ['status', 'design_image', 'admin_comment']
        labels = {
            'status': 'Новый статус',
            'image': 'Изображение дизайна (требуется для статуса "Выполнено")',
            'admin_comment': 'Комментарий (требуется для статуса "Принято в работу")',
        }
        widgets = {
            'admin_comment': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Введите комментарий для пользователя...'
            }),
        }

    def clean(self):
        """
        Дополнительная валидация формы при сохранении.
        Проверяет, что при смене статуса на 'completed' загружено изображение дизайна,
        а при смене на 'in_progress' введен комментарий.
        """
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        design_image = cleaned_data.get('image')
        admin_comment = cleaned_data.get('admin_comment')

        if status == 'complete' and not design_image:
            self.add_error('image', 'Для статуса "Выполнено" необходимо прикрепить изображение дизайна.')
        if status == 'in-progress' and not admin_comment:
            self.add_error('admin_comment', 'Для статуса "Принято в работу" необходимо указать комментарий.')

        return cleaned_data

    def __init__(self, *args, **kwargs):
        """
        Инициализирует форму.
        Устанавливает начальные значения виджетов и ограничения на выбор статуса.
        """
        super().__init__(*args, **kwargs)
        # Сделаем поля design_image и admin_comment необязательными по умолчанию,
        # валидация в clean() определит, когда они обязательны.
        self.fields['image'].required = False
        self.fields['admin_comment'].required = False

        def can_change_status(self, new_status):
            """Проверка возможности смены статуса"""
            if self.status != 'new':
                return False

            # Для новых заявок всегда можно попытаться сменить статус
            # Валидация будет в форме/представлении
            return new_status in ['in-progress', 'complete']
