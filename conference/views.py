from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm, RegistrationForm, BookingRequestForm, ReviewForm, AdminBookingUpdateForm
from .models import Venue, Review, BookingRequest


def check_admin_access(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.is_staff:
        messages.error(request, 'Доступ разрешён только администратору.')
        return redirect('login')

    return None


def home_view(request):
    context = {
        'venues': Venue.objects.all()[:4],
        'reviews': Review.objects.select_related('user', 'booking_request')[:4],
        'stats': {
            'venues': Venue.objects.count(),
            'requests': BookingRequest.objects.count(),
            'completed': BookingRequest.objects.filter(
                status=BookingRequest.STATUS_COMPLETED
            ).count(),
        },
    }
    return render(request, 'conference/home.html', context)


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_requests')
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.is_staff:
                return redirect('admin_requests')
            return redirect('dashboard')

        messages.error(request, 'Неверный логин или пароль.')
    else:
        form = LoginForm(request)

    return render(request, 'conference/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно.')
            return redirect('dashboard')
    else:
        form = RegistrationForm()

    return render(request, 'conference/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    booking_requests = (
        BookingRequest.objects.filter(user=request.user)
        .select_related('venue')
        .prefetch_related('review')
    )

    context = {
        'booking_requests': booking_requests,
        'booking_stats': {
            'total': booking_requests.count(),
            'new': booking_requests.filter(status=BookingRequest.STATUS_NEW).count(),
            'scheduled': booking_requests.filter(
                status=BookingRequest.STATUS_SCHEDULED
            ).count(),
            'completed': booking_requests.filter(
                status=BookingRequest.STATUS_COMPLETED
            ).count(),
        },
    }
    return render(request, 'conference/dashboard.html', context)


@login_required
def create_request_view(request):
    if request.method == 'POST':
        form = BookingRequestForm(request.POST)
        if form.is_valid():
            booking_request = form.save(commit=False)
            booking_request.user = request.user
            booking_request.save()
            messages.success(request, 'Заявка на бронирование создана.')
            return redirect('dashboard')
    else:
        form = BookingRequestForm()

    context = {
        'form': form,
        'venues': Venue.objects.all(),
    }
    return render(request, 'conference/create_request.html', context)


@login_required
def review_create_view(request, pk):
    booking_request = get_object_or_404(
        BookingRequest.objects.select_related('user'),
        pk=pk,
        user=request.user,
    )

    if request.method != 'POST':
        return redirect('dashboard')

    if not booking_request.can_leave_review:
        messages.error(
            request,
            'Отзыв доступен только после изменения статуса заявки.',
        )
        return redirect('dashboard')

    review = Review(user=request.user, booking_request=booking_request)
    form = ReviewForm(request.POST, instance=review)

    if form.is_valid():
        form.save()
        messages.success(request, 'Спасибо, отзыв сохранён.')
    else:
        messages.error(request, 'Проверьте форму отзыва.')

    return redirect('dashboard')


def admin_requests_view(request):
    denied_response = check_admin_access(request)
    if denied_response:
        return denied_response

    booking_requests = (
        BookingRequest.objects.select_related('user', 'venue')
        .prefetch_related('review')
    )

    search_query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    payment = request.GET.get('payment', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    ordering = request.GET.get('ordering', '-created_at').strip()

    if search_query:
        booking_requests = booking_requests.filter(
            Q(conference_title__icontains=search_query)
            | Q(user__full_name__icontains=search_query)
            | Q(user__username__icontains=search_query)
            | Q(venue__name__icontains=search_query)
        )

    if status:
        booking_requests = booking_requests.filter(status=status)

    if payment:
        booking_requests = booking_requests.filter(payment_method=payment)

    if date_from:
        booking_requests = booking_requests.filter(event_date__gte=date_from)

    if date_to:
        booking_requests = booking_requests.filter(event_date__lte=date_to)

    if ordering not in {
        'created_at',
        '-created_at',
        'event_date',
        '-event_date',
        'status',
    }:
        ordering = '-created_at'

    booking_requests = booking_requests.order_by(ordering)

    status_summary = {
        'new': booking_requests.filter(status=BookingRequest.STATUS_NEW).count(),
        'scheduled': booking_requests.filter(
            status=BookingRequest.STATUS_SCHEDULED
        ).count(),
        'completed': booking_requests.filter(
            status=BookingRequest.STATUS_COMPLETED
        ).count(),
    }

    paginator = Paginator(booking_requests, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'booking_requests': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'status_choices': BookingRequest.STATUS_CHOICES,
        'payment_choices': BookingRequest.PAYMENT_CHOICES,
        'status_summary': status_summary,
        'current_filters': {
            'q': search_query,
            'status': status,
            'payment': payment,
            'date_from': date_from,
            'date_to': date_to,
            'ordering': ordering,
        },
    }
    return render(request, 'conference/admin_requests.html', context)


def admin_request_detail_view(request, pk):
    denied_response = check_admin_access(request)
    if denied_response:
        return denied_response

    booking_request = get_object_or_404(
        BookingRequest.objects.select_related('user', 'venue')
        .prefetch_related('review'),
        pk=pk,
    )

    if request.method == 'POST':
        form = AdminBookingUpdateForm(request.POST, instance=booking_request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Статус заявки обновлён.')
            return redirect('admin_requests')
    else:
        form = AdminBookingUpdateForm(instance=booking_request)

    context = {
        'form': form,
        'object': booking_request,
    }
    return render(request, 'conference/admin_request_detail.html', context)
