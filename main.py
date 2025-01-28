import icalendar
import datetime
import json
import os
import time
import requests
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
cutoff = datetime.date(2024, 8, 31)
ical_url="https://calendar.google.com/calendar/ical/leobaeck.net_sqm2v9h1k13gl8nps32iba34q8%40group.calendar.google.com/public/basic.ics"

# def read_ical_local(ical_file):
#     with open(ical_file, 'r', encoding="utf-8") as ical_file:
#         return icalendar.Calendar.from_ical(ical_file.read())

def read_ical(url):
    response = requests.get(url)
    return icalendar.Calendar.from_ical(response.text)

def process_events():
    filtered_events = []

    for event in read_ical(ical_url).walk('vevent'):
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
    
    # with open('filtered.json', 'w', encoding='utf-8') as json_file:
    #     json_file.write(json.dumps(filtered_events, default=str, indent=4, ensure_ascii=False))
    
    filtered_events = sorted(filtered_events, key=lambda x: x['start'])
    return filtered_events

def update_json():

    events = process_events()

    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 65536,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-thinking-exp-01-21",
        generation_config=generation_config,
        system_instruction="אתה הולך לקבל JSON המכיל את רשימת האירועים של שכבת ח. עליך למיין כח אחד מהאירועים, לפי 2 מאפיינים:\n1. כיתות - עליך לקבוע לאילו כיתות האירוע רלוונטי, ואתה מוסיף אתה זה לJSON באופן הבא:\n\n\"classes\": [4, 5, 6, 7, 8, 9],\nאם אתה יודע בוודאות לאילו כיתות רלוונטי האירוע, הכנס את מספרי הכיתות, ללא האות ח (למשל אם מצוין שהאירוע רלוונטי לח5, הכנס [5]. במידה והאירוע רלווטי לכולם, הכנס null. במידה ואינך בטוח, הכס סוגרים [] ריקות. \nאל תבלבל בין מספר הכיתה לכיתה. רלוונטי לי מספר הכיתה, למשל ח*5* או ח*1*. כל האירועים הJSON הם של כיתות ח, השאלה אילו מספרי כיתות\n\n2. יחידות (שיעורים). עליך לקבוע לאיזה יחידה שייך כל אירוע, ואתה מוסיף זאת לJSON כך:\n\n\"units\": [2, 3],\nאם אתה יודע בוודאות באילו יחידות האירוע מתרחש, הכנס את מספר/י היחיד/ות. במידה והאירוע נמשך לכל היום, כמו מסע חינוכי (טיול שנתי), הכנס null. במידה ואינך בטוח, הכס סוגרים [] ריקות.\n\nDO NOT RESPOND WITH MARKDOWN, DO NOT USE ```json```",
    )

    chat_session = model.start_chat(
        history=[
        ]
    )

    response = chat_session.send_message(json.dumps(events, default=str, indent=4, ensure_ascii=False))

    with open('final.json', 'w', encoding='utf-8') as json_file:
        lines = response.text.splitlines()
        if lines and lines[0].startswith('```json'): # todo - understand this code 
            lines = lines[1:]
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]
        json_file.write('\n'.join(lines))

    

while True:
    try:
        update_json()
        print("Updated JSON")
    except Exception as e:
        print("Error: ", e)
    time.sleep(86400)