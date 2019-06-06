from reciperadar.services.calendar import get_calendar_api


class CalendarWatcher(object):

    def watch(self):
        calendar = get_calendar_api()
        delivery = {
            'id': 'default',
            'type': 'webhook',
            'address': 'https://staging.reciperadar.com/webhooks/calendar',
        }
        channel = calendar.events().watch(
            calendarId='calendar@reciperadar.com',
            body=delivery
        ).execute()
        print(channel)


CalendarWatcher().watch()
