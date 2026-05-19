from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

username_validator = RegexValidator(
    regex=r'^[A-Za-z0-9]+$',
    message='Логин может содержать только латинские буквы и цифры.',
)

phone_validator = RegexValidator(
    regex=r'^\+?\d{10,15}$',
    message='Введите телефон в формате +79991234567 или 89991234567.',
)

class User(AbstractUser):
    first_name = None
    last_name = None

    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        validators=[username_validator],
        help_text='Минимум 6 символов, только латиница и цифры.',
    )
    full_name = models.CharField(
        'ФИО',
        max_length=255
    )
    phone = models.CharField(
        'Телефон',
        max_length=16,
        validators=[phone_validator]
    )
    email = models.EmailField(
        'Электронная почта',
        unique=True
    )

    REQUIRED_FIELDS = ['email', 'full_name', 'phone']


class Venue(models.Model):
    name = models.CharField(
        'Название помещения',
        max_length=150
    )
    location = models.CharField(
        'Расположение',
        max_length=200
    )
    capacity = models.PositiveIntegerField(
        'Вместимость'
    )
    hourly_rate = models.DecimalField(
        'Стоимость в час',
        max_digits=10,
        decimal_places=2
    )
    short_description = models.TextField(
        'Краткое описание'
    )
    amenities = models.TextField(
        'Удобства'
    )
    image = models.CharField(
        'Изображение',
        max_length=255,
    )
    display_order = models.PositiveIntegerField(
        'Порядок показа',
        default=0
    )


class BookingRequest(models.Model):
    PAYMENT_CARD = 'card'
    PAYMENT_CASH = 'cash'
    PAYMENT_INVOICE = 'invoice'
    PAYMENT_CHOICES = [
        (PAYMENT_CARD, 'Банковская карта'),
        (PAYMENT_CASH, 'Наличные'),
        (PAYMENT_INVOICE, 'Безналичный расчёт'),
    ]

    STATUS_NEW = 'new'
    STATUS_SCHEDULED = 'scheduled'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_NEW, 'Новая'),
        (STATUS_SCHEDULED, 'Мероприятие назначено'),
        (STATUS_COMPLETED, 'Мероприятие завершено'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='booking_requests',
        verbose_name='Пользователь'
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.PROTECT,
        related_name='booking_requests',
        verbose_name='Помещение'
    )
    conference_title = models.CharField(
        'Название мероприятия',
        max_length=200
    )
    event_date = models.DateField(
        'Дата проведения'
    )
    preferred_time = models.TimeField(
        'Предпочтительное время'
    )
    attendees = models.PositiveIntegerField(
        'Количество участников',
        default=10
    )
    payment_method = models.CharField(
        'Способ оплаты',
        max_length=20,
        choices=PAYMENT_CHOICES,
        default=PAYMENT_CARD
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW
    )
    special_requests = models.TextField(
        'Комментарий к заявке',
        blank=True
    )
    admin_comment = models.TextField(
        'Комментарий администратора',
        blank=True
    )
    created_at = models.DateTimeField(
        'Создано',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        'Обновлено',
        auto_now=True
    )

    def clean(self):
        errors = {}
        if self.event_date and self.event_date < timezone.localdate():
            errors['event_date'] = 'Дата бронирования не может быть в прошлом.'
        if self.venue_id and self.attendees and self.attendees > self.venue.capacity:
            errors['attendees'] = f'Для этой площадки доступно максимум {self.venue.capacity} гостей.'
        if errors:
            raise ValidationError(errors)

    @property
    def can_leave_review(self):
        return self.status != self.STATUS_NEW and not hasattr(self, 'review')

    @property
    def status_badge_class(self):
        if self.status == self.STATUS_NEW:
            return 'badge rounded-pill text-bg-danger'
        if self.status == self.STATUS_SCHEDULED:
            return 'badge rounded-pill text-bg-primary'
        if self.status == self.STATUS_COMPLETED:
            return 'badge rounded-pill text-bg-success'
        return 'badge rounded-pill text-bg-secondary'


class Review(models.Model):
    booking_request = models.OneToOneField(
        BookingRequest,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='Заявка',
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reviews', 
        verbose_name='Автор'
        )
    rating = models.PositiveSmallIntegerField(
        'Оценка'
        )
    comment = models.TextField(
        'Отзыв'
        )
    created_at = models.DateTimeField(
        'Создано', auto_now_add=True
        )

    def clean(self):
        if self.booking_request.user_id != self.user_id:
            raise ValidationError('Отзыв может оставить только владелец заявки.')

        if self.booking_request.status == BookingRequest.STATUS_NEW:
            raise ValidationError('Оставить отзыв можно только после изменения статуса заявки.')