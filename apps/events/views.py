from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Event, EventCategory, EventHistory
from .forms import EventForm
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from datetime import datetime, date, timedelta
from django.db.models import Q, Model
from functools import wraps

def log_event_history(event, user, action, changes=None):
    if action == 'created':
        EventHistory.objects.create(
            event=event,
            user=user,
            action=action
        )
    elif action == 'updated' and changes:
        for field, values in changes.items():
            EventHistory.objects.create(
                event=event,
                user=user,
                action=action,
                field_changed=field,
                old_value=str(values['old']),
                new_value=str(values['new'])
            )

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

    if view_type == 'day':
        start_date = base_date
        end_date = base_date
    elif view_type == 'week':
        start_date = base_date - timedelta(days=base_date.isoweekday() % 7)
        end_date = start_date + timedelta(days=6)
    elif view_type == 'year':
        start_date = date(base_date.year, 1, 1)
        end_date = date(base_date.year, 12, 31)
    else:
        start_of_month = base_date.replace(day=1)
        start_date = start_of_month - timedelta(days=start_of_month.isoweekday() % 7)
        end_date = start_date + timedelta(days=41)

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

@api_auth_required
def api_event_history(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if not is_editor(request.user) and (event.status == 'CANCELLED' or event.privacy == 'PRIVATE'):
        return JsonResponse({'error': 'You do not have permission to view this event history.'}, status=403)

    history = event.history_logs.select_related('user').order_by('-timestamp')
    history_data = []
    for log in history:
        history_data.append({
            'id': log.id,
            'user': log.user.get_full_name() or log.user.username if log.user else 'System',
            'action': log.action,
            'field_changed': log.field_changed,
            'old_value': log.old_value,
            'new_value': log.new_value,
            'timestamp': log.timestamp.strftime('%b %d, %Y, %I:%M %p'),
        })
    return JsonResponse(history_data, safe=False)

@login_required
def event_detail_view(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if not is_editor(request.user) and (event.status == 'CANCELLED' or event.privacy == 'PRIVATE'):
        raise PermissionDenied("You do not have permission to view this event.")
    
    history_logs = event.history_logs.select_related('user').order_by('-timestamp')

    context = {
        'event': event,
        'history_logs': history_logs,
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
            log_event_history(event, request.user, 'created')
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
            changes = {}
            if form.has_changed():
                for field_name in form.changed_data:
                    old_value = form.initial.get(field_name)
                    new_value = form.cleaned_data.get(field_name)
                    
                    old_value_display = old_value
                    new_value_display = new_value

                    if isinstance(new_value, Model):
                        new_value_display = str(new_value)
                        if old_value:
                            try:
                                old_value_display = str(new_value.__class__.objects.get(pk=old_value))
                            except new_value.__class__.DoesNotExist:
                                old_value_display = "N/A"
                        else:
                            old_value_display = None
                    
                    if field_name in ['status', 'privacy']:
                        choices = dict(Event.STATUS_CHOICES if field_name == 'status' else Event.PRIVACY_CHOICES)
                        old_value_display = choices.get(old_value, old_value)
                        new_value_display = choices.get(new_value, new_value)

                    field_label = form.fields[field_name].label or field_name.replace('_', ' ').title()
                    
                    if str(old_value_display) != str(new_value_display):
                        changes[field_label] = {
                            'old': old_value_display or "Not set",
                            'new': new_value_display or "Not set"
                        }

            updated_event = form.save()

            if changes:
                log_event_history(updated_event, request.user, 'updated', changes=changes)

            messages.success(request, 'Event updated successfully.')
            return redirect('events:calendar')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
            return redirect('events:calendar')
    return redirect('events:calendar')