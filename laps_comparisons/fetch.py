import fastf1
import json
from fastf1.core import Session
from fastf1.events import Event

def get_input() -> tuple[str, int, list[str]]:
    """Load the session config and return country and year"""
    config = load_session()
    return config['country'], config['year'], config['drivers'].split()

def load_session() -> dict[str, int, str]:
    """Load the session configuration from a JSON file."""
    session_file = 'session.json'
    with open(session_file, 'r') as f:
        return json.load(f)

def get_data(year: int, country: str) -> tuple[Session, Event]:
    """Fetch the FastF1 session and event data."""
    session_data = fastf1.get_session(year, country, 'Race')
    session_data.load()
    event = fastf1.get_event(year, country)

    return session_data, event

def get_event_info(session_data: Session, event: Event) -> dict[str, str | int]:
    return {
        'grand_prix' : session_data.session_info['Meeting']['Name'],
        'location' : session_data.session_info['Meeting']['Circuit']['ShortName'],
        'country_name' : session_data.session_info['Meeting']['Country']['Name'],
        'country_code' : session_data.session_info['Meeting']['Country']['Code'],
        'round_number' : event['RoundNumber'],
        'session' : session_data.session_info['Type'],
        'year' : session_data.session_info['StartDate'].year
    }