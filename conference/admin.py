from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import BookingRequest, Review, User, Venue


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'full_name', 'email', 'phone', 'is_staff')
    search_fields = ('username', 'full_name', 'email', 'phone')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Контакты', {'fields': ('full_name', 'email', 'phone')}),
        (
            'Права доступа',
            {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')},
        ),
        ('Служебная информация', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('username', 'full_name', 'email', 'phone', 'password1', 'password2'),
            },
        ),
    )


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity', 'hourly_rate')
    search_fields = ('name', 'location')


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ('conference_title', 'user', 'venue', 'event_date', 'preferred_time', 'status')
    list_filter = ('status', 'payment_method', 'event_date')
    search_fields = ('conference_title', 'user__username', 'user__full_name', 'venue__name')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('booking_request', 'user', 'rating', 'created_at')
    search_fields = ('booking_request__conference_title', 'user__username')
