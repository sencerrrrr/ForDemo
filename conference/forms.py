from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import BookingRequest, Review, User


def add_bootstrap_classes(form):
    for field in form.fields.values():
        if isinstance(field.widget, forms.Select):
            field.widget.attrs['class'] = 'form-select'
        else:
            field.widget.attrs['class'] = 'form-control'


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label='Пароль',
        strip=False,
        help_text='Минимум 8 символов.',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Минимум 8 символов',
                'autocomplete': 'new-password',
            }
        ),
    )

    class Meta:
        model = User
        fields = ['username', 'password', 'full_name', 'phone', 'email']
        labels = {
            'username': 'Логин',
            'full_name': 'ФИО',
            'phone': 'Телефон',
            'email': 'Электронная почта',
        }
        help_texts = {
            'username': 'Минимум 6 символов, только латиница и цифры.',
            'phone': 'Например: +79991234567',
        }
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Ivan'}),
            'full_name': forms.TextInput(attrs={'placeholder': 'Иванов Иван Иванович'}),
            'phone': forms.TextInput(attrs={'placeholder': '+79991234567'}),
            'email': forms.EmailInput(attrs={'placeholder': 'ivan@mail.ru'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)

    def clean_username(self):
        username = self.cleaned_data['username']

        if len(username) < 6:
            raise ValidationError('Логин должен содержать минимум 6 символов.')

        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('Этот логин уже занят.')

        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        validate_password(password)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Ваш логин',
                'autocomplete': 'username',
            }
        ),
    )
    password = forms.CharField(
        label='Пароль',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Ваш пароль',
                'autocomplete': 'current-password',
            }
        ),
    )

    error_messages = {
        'invalid_login': 'Неверный логин или пароль.',
        'inactive': 'Этот аккаунт отключён.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)


class BookingRequestForm(forms.ModelForm):
    class Meta:
        model = BookingRequest
        fields = [
            'conference_title',
            'venue',
            'event_date',
            'preferred_time',
            'attendees',
            'payment_method',
            'special_requests',
        ]
        labels = {
            'conference_title': 'Название конференции',
            'venue': 'Помещение',
            'event_date': 'Дата',
            'preferred_time': 'Предпочтительное время',
            'attendees': 'Количество участников',
            'payment_method': 'Способ оплаты',
            'special_requests': 'Дополнительные пожелания',
        }
        help_texts = {
            'event_date': 'Используйте календарь для выбора даты.',
            'payment_method': 'Выберите удобный способ оплаты.',
        }
        widgets = {
            'conference_title': forms.TextInput(attrs={'placeholder': 'Весенняя IT-конференция'}),
            'event_date': forms.DateInput(attrs={'type': 'date'}),
            'preferred_time': forms.TimeInput(attrs={'type': 'time'}),
            'attendees': forms.NumberInput(attrs={'min': 1, 'max': 500}),
            'special_requests': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'Например: нужен проектор и приветственная зона.',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        labels = {
            'rating': 'Оценка',
            'comment': 'Комментарий',
        }
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} / 5') for i in range(5, 0, -1)]),
            'comment': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Расскажите, как прошло мероприятие.',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)


class AdminBookingUpdateForm(forms.ModelForm):
    class Meta:
        model = BookingRequest
        fields = ['status', 'admin_comment']
        labels = {
            'status': 'Статус заявки',
            'admin_comment': 'Комментарий администратора',
        }
        help_texts = {
            'status': 'Выберите нужный статус из списка.',
        }
        widgets = {
            'admin_comment': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'Например: зал подтверждён на 14:00.',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)
