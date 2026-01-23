from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os
import json
from backend.config import Config

class CalendarService:
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    def __init__(self):
        self.credentials_file = Config.CREDENTIALS_FILE
        self.creds = None
        self._load_credentials()

    def _load_credentials(self):
        """Load saved credentials if they exist"""
        if os.path.exists(self.credentials_file):
            try:
                with open(self.credentials_file, 'r') as f:
                    cred_data = json.load(f)
                    self.creds = Credentials(
                        token=cred_data.get('token'),
                        refresh_token=cred_data.get('refresh_token'),
                        token_uri=cred_data.get('token_uri'),
                        client_id=cred_data.get('client_id'),
                        client_secret=cred_data.get('client_secret'),
                        scopes=cred_data.get('scopes')
                    )
            except Exception as e:
                print(f"Error loading credentials: {e}")
                self.creds = None

    def _save_credentials(self, creds):
        """Save credentials to file"""
        os.makedirs(os.path.dirname(self.credentials_file), exist_ok=True)
        cred_dict = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        }
        with open(self.credentials_file, 'w') as f:
            json.dump(cred_dict, f, indent=2)

    def get_auth_url(self) -> str:
        """Generate authorization URL"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": Config.GOOGLE_CLIENT_ID,
                    "client_secret": Config.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": [Config.GOOGLE_REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=self.SCOPES,
            redirect_uri=Config.GOOGLE_REDIRECT_URI
        )

        auth_uri, _ = flow.authorization_url(prompt='consent')
        return auth_uri

    def handle_oauth_callback(self, authorization_code: str):
        """Exchange authorization code for credentials"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": Config.GOOGLE_CLIENT_ID,
                    "client_secret": Config.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": [Config.GOOGLE_REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=self.SCOPES,
            redirect_uri=Config.GOOGLE_REDIRECT_URI
        )

        flow.fetch_token(code=authorization_code)
        self.creds = flow.credentials
        self._save_credentials(self.creds)

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.creds is not None and self.creds.valid

    def create_event(self, task: dict) -> str:
        """Create an event"""
        if not self.is_authenticated():
            raise Exception("Not authenticated with Google Calendar")

        service = build('calendar', 'v3', credentials=self.creds)

        if task.get('due_date'):
            start_date = task['due_date']
            if task.get('due_time'):
                start_datetime = f"{start_date}T{task['due_time']}:00"

                dur_mins = task.get('duration_estimate', 60)
                start_dt = datetime.fromisoformat(start_datetime)
                end_dt = start_dt + timedelta(minutes=dur_mins)
                end_datetime = end_dt.isoformat()

                event = {
                    'summary': task['title'],
                    'description': task['description', ''],
                    'start': {
                        'dateTime': start_datetime,
                        'timeZone': 'America/New_York',
                    },
                    'end': {
                        'dateTime': end_datetime,
                        'timeZone': 'America/New_York',
                    }
                }
            else:
                event = {
                    'summary': task['title'],
                    'description': task['description', ''],
                    'start': {'date' : start_date},
                    'end': {'date' : start_date},
                }
        else:
            today = datetime.now().date().isoformat()
            event = {
                'summary': task['title'],
                'description': task.get('description', ''),
                'start': {'date': today},
                'end': {'date': today},
            }
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        return created_event['id']

    def get_upcoming_events(self, max_results: int = 10) -> list:
        """Get upcoming events"""
        if not self.is_authenticated():
            return []

        service = build('calendar', 'v3', credentials=self.creds)

        now = datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime',
        ).execute()

        events = events_result.get('items', [])

        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            formatted_events.append({
                'id': event['id'],
                'summary': event.get('summary', 'Untitled'),
                'start_time': start,
                'description': event.get('description', ''),
            })

        return formatted_events

    def delete_event(self, event_id: str):
        """Delete an event"""
        if not self.is_authenticated():
            raise Exception("Not authenticated with Google Calendar")

        service = build('calendar', 'v3', credentials=self.creds)
        service.events().delete(calendarId='primary', eventId=event_id).execute()