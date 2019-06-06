from google.oauth2.service_account import Credentials
from googleapiclient import discovery


def get_calendar_api():
    credentials = Credentials.from_service_account_file(
        filename='credentials/calendar_secret.json',
        scopes=['https://www.googleapis.com/auth/calendar.events']
    ).with_subject('calendar@reciperadar.com')
    return discovery.build('calendar', 'v3', credentials=credentials)
