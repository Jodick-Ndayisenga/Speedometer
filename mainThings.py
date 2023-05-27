from __future__ import print_function
#from calendar import month
#And we import datetime module to help us
import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import os
#import time
import pyttsx3
import speech_recognition as sr
import pytz

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ['january', 'february', 'march', 'april', 'may', 'jun',
          'july', 'august', 'september', 'october', 'november', 'december']
DAYS = ['mondays', 'tuesday', 'wednsday',
        'thursday', 'friday', 'saturday', 'sunday']
EXTENSIONS = ['rd', 'th', 'st', 'nd']


def Speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ''
        try:
            said = r.recognize_google(audio)
            print(said)
        except Exception as e:
            print('Exception: ' + str(e))

        return said


#print('Talk Now!')


def authenticate_google():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        service = build('calendar', 'v3', credentials=creds)
        return service


def get_event(day, service):
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date=end_date.astimezone(utc)
    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(),timeMax=end_date.isoformat(),
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        Speak('No upcoming events found.')

    # Prints the start and name of the next 10 events
    else:
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split('T')[1].split('-')[0])
            if int(start_time.split(':')[0])<12:
                start_time = start_time + 'am'

            else:
                start_time= str(int(start_time.split(':')[0])<12)
                start_time = start_time + 'pm'
            
            Speak(event['summary']+'at'+start_time)


def get_date(text):
    text = text.lower()
    today = datetime.date.today()

    if text.count('today') > 0:
        return today
    day = -1
    dayOfWeek = -1
    month = -1
    year = today.year
    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word)+1

        elif word in DAYS:
            dayOfWeek = DAYS.index(word)

        elif word.isdigit():
            day = int(word)
        else:
            for ext in EXTENSIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass
    if month < today.month and month != -1:
        year = year+1

    if day < today.day and month != -1 and day != -1:
        month = month + 1

    if day == -1 and month == -1 and dayOfWeek != -1:
        current_day_of_week = today.weekday()
        dif = dayOfWeek - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count('next') >= 1:
                dif += 7
        return today + datetime.timedelta(dif)
    #return datetime.date(month=month, day=day, year=year)

SERVICE=authenticate_google()
print('Start asking your question')
text = get_audio()
WORDS = ['what do i have', 'do i have plans', 'am i busy']
for short_words in WORDS:
    if short_words in text.lower():
        date = get_date(text)
        if date:
            get_event(date, SERVICE)
        else:
            Speak('Please, I did not here well what you said')
