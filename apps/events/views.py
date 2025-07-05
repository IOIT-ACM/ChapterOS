from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Event, EventCategory
from .forms import EventForm
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from datetime import datetime, date, timedelta
from django.db.models import Q
from functools import wraps

def is_editor(user):
    if user.is_authenticated:
        return user.groups.filter(name__in=['Admin', 'Core']).exists()
    return False

def api_auth_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required.'}, status=401)
        
        is_visitor_only = request.user.groups.filter(name='Visitor').exists() and request.user.groups.count() == 1
        if is_visitor_only:
            return JsonResponse({'error': 'You do not have permission to access this data.'}, status=403)
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
def calendar_view(request):
    form = EventForm()
    context = {
        'form': form,
        'is_editor': is_editor(request.user)
    }
    return render(request, 'events/calendar.html', context)

@api_auth_required
def api_event_categories(request):
    categories = EventCategory.objects.all().values('id', 'name', 'color')
    return JsonResponse(list(categories), safe=False)

@api_auth_required
def api_event_statuses(request):
    statuses = Event.STATUS_CHOICES
    return JsonResponse(statuses, safe=False)

@api_auth_required
def api_events(request):
    view_type = request.GET.get('view', 'month')
    date_str = request.GET.get('date')
    
    try:
        base_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        base_date = date.today()

    if view_type == 'month':
        start_date = base_date.replace(day=1)
        last_day = (start_date.replace(month=start_date.month % 12 + 1, day=1) - timedelta(days=1))
        end_date = last_day
    elif view_type == 'week':
        start_date = base_date - timedelta(days=base_date.weekday()) # Monday
        end_date = start_date + timedelta(days=6) # Sunday
    elif view_type == 'day':
        start_date = end_date = base_date
    else: # Fallback for Agenda/Year for now
        start_date = base_date
        end_date = base_date + timedelta(days=30)

    queryset = Event.objects.select_related('category', 'created_by').filter(
        Q(start_date__lte=end_date, end_date__gte=start_date) |
        Q(start_date__range=(start_date, end_date), end_date__isnull=True)
    ).order_by('start_date', 'start_time')

    if not is_editor(request.user):
        queryset = queryset.filter(privacy='PUBLIC', status__in=['PLANNED', 'IN_PROGRESS', 'COMPLETED'])

    events_data = []
    for event in queryset:
        events_data.append({
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'start_date': event.start_date.isoformat() if event.start_date else None,
            'end_date': event.end_date.isoformat() if event.end_date else None,
            'start_time': event.start_time.strftime('%H:%M') if event.start_time else None,
            'end_time': event.end_time.strftime('%H:%M') if event.end_time else None,
            'is_all_day': event.is_all_day,
            'location': event.location,
            'status': event.status,
            'get_status_display': event.get_status_display(),
            'privacy': event.privacy,
            'category_id': event.category.id if event.category else None,
            'category_name': event.category.name if event.category else 'Uncategorized',
            'category_color': event.category.color if event.category else '#4A5568',
            'created_by_name': event.created_by.get_full_name() or event.created_by.username,
            'created_by_id': event.created_by.id,
        })

    return JsonResponse(events_data, safe=False)

@login_required
def event_detail_view(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if not is_editor(request.user) and (event.status == 'CANCELLED' or event.privacy == 'PRIVATE'):
        raise PermissionDenied("You do not have permission to view this event.")
    context = {
        'event': event,
    }
    return render(request, 'events/event_detail.html', context)

@user_passes_test(is_editor)
def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event added successfully.')
            return redirect('events:calendar')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
            return redirect('events:calendar')
    return redirect('events:calendar')

@user_passes_test(is_editor)
def edit_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully.')
            return redirect('events:calendar')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
            return redirect('events:calendar')
    return redirect('events:calendar')