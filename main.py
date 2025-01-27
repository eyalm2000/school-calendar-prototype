import icalendar
import datetime
import json

with open('basic.ics', 'r', encoding="utf-8") as ical_file:
    cal = icalendar.Calendar.from_ical(ical_file.read())

filtered_events = []
cutoff = datetime.date(2024, 8, 31)

for event in cal.walk('vevent'):
    start_date = event.get('dtstart').dt
    if isinstance(start_date, datetime.datetime): 
        start_date = start_date.date()
    if start_date > cutoff:
        filtered_events.append({
            'start': start_date,
            'end': event.get('dtend').dt,
            'summary': event.get('summary'),
            'description': event.get('description')
        })
filtered_events = sorted(filtered_events, key=lambda x: x['start'])
with open('filtered.json', 'w') as json_file:
    json_file.write(json.dumps(filtered_events, default=str, indent=4))