from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
import re
from .models import  DesignRequest, Category, CustomUser

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password_confirm = forms.CharField(label="Пароль (повторно)", widget=forms.PasswordInput)
    username = forms.CharField(label="Логин", help_text='')

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'patronymic', 'username', 'email', 'password', 'password_confirm',
                  'agreement')
        labels = {'first_name': 'Имя', 'last_name': 'Фамилия', 'patronymic': 'Отчество', 'email': 'Почта',
                  'agreement': 'Я согласен на обработку персональных данных'}

        error_messages = {
            'username': {
                'unique': "Пользователь с таким логином уже зарегистрирован",
            },
        }

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name and not re.fullmatch(r"^[а-яА-Я -]+$", first_name):
            raise forms.ValidationError("Имя должно содержать только кириллицу, дефисы и пробелы")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name and not re.fullmatch(r"^[а-яА-Я -]+$", last_name):
            raise forms.ValidationError("Фамилия должна содержать только кириллицу, дефисы и пробелы")
        return last_name

    def clean_patronymic(self):
        patronymic = self.cleaned_data.get('patronymic')
        if patronymic and not re.fullmatch(r"^[а-яА-Я -]+$", patronymic):
            raise forms.ValidationError("Отчество должно содержать только кириллицу, дефисы и пробелы")
        return patronymic

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and not re.fullmatch(r"^[a-zA-z-]+$", username):
            raise forms.ValidationError("Логин должен содержать только латиницу и дефисы")
        return username

    def clean(self):
        super().clean()
        if self.cleaned_data.get('password') != self.cleaned_data.get('password_confirm'):
            raise ValidationError({'password_confirm': 'Введенные пароли не совпадают'})
        return self.cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

    def clean_agreement(self):
        agreement = self.cleaned_data.get('agreement')
        if not agreement:
            raise forms.ValidationError('Вы должны согласиться на обработку персональных данных')
        return agreement

def file_size(value):
    limit = 2 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('Размер файла не должен превышать 2Мб.')

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Логин')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput())

class DesignRequestForm(forms.ModelForm):
    class Meta:
        model = DesignRequest
        fields = ['title', 'description', 'category', 'image']
        labels = {'image': 'Фото помещения или план'}

class ChangeStatusForm(forms.ModelForm):
    """     Форма для изменения статуса заявки администратором.   """
    class Meta:
        model = DesignRequest
        fields = ['status', 'design_image', 'admin_comment']
        labels = {
            'status': 'Новый статус',
            'design_image': 'Изображение дизайна (требуется для статуса "Выполнено")',
            'admin_comment': 'Комментарий (требуется для статуса "Принято в работу")',
        }

    def clean(self):

        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        design_image = cleaned_data.get('design_image')
        admin_comment = cleaned_data.get('admin_comment')

        if status == 'complete' and not design_image:
            self.add_error('image', 'Для статуса "Выполнено" необходимо прикрепить изображение дизайна.')
        if status == 'in-progress' and not admin_comment:
            self.add_error('admin_comment', 'Для статуса "Принято в работу" необходимо указать комментарий.')

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['design_image'].required = False
        self.fields['admin_comment'].required = False

        def can_change_status(self, new_status):
            if self.status != 'new':
                return False
            return new_status in ['in-progress', 'complete']
