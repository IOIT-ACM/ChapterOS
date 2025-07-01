from django.shortcuts import render
from django.http import JsonResponse
from icalendar import Calendar
from datetime import datetime, timezone
import os
import requests

ICAL_URL = os.getenv('ICAL_URL')

def fetch_events():
    try:
        response = requests.get(ICAL_URL, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    except Exception as e:
        print("Error fetching ICS:", e)
        return []

    cal = Calendar.from_ical(response.content)
    events = []

    for component in cal.walk():
        if component.name == "VEVENT":
            start = component.get("dtstart").dt
            end = component.get("dtend").dt
            title = component.get("summary", "No Title")
            desc = component.get("description", "")
            url = component.get("url", "")

            events.append({
                "title": str(title),
                "start": start.isoformat(),
                "end": end.isoformat() if end else start.isoformat(),
                "description": str(desc),
                "url": str(url),
            })

    return events

def calendar_view(request):
    return render(request, "calendar_app/index.html")

def calendar_events(request):
    return JsonResponse(fetch_events(), safe=False)
