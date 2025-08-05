import json
import fastf1
from fastf1.core import Session
from fastf1.events import Event
from typing import Tuple, Dict


def get_input() -> Tuple[str, int]:
    """Load the session config and return country and year."""
    config = load_session()
    return config['country'], config['year']


def load_session() -> Dict[str, int]:
    """Load the session configuration from a JSON file."""
    file_path = "session.json"
    with open(file_path, 'r') as f:
        return json.load(f)


def get_data(country: str, year: int) -> Tuple[Session, Event]:
    """Fetch the FastF1 session and event data."""
    session_data = fastf1.get_session(year, country, 'Race')
    session_data.load()
    event = fastf1.get_event(year, country)

    return session_data, event


def get_event_info(session_data: Session, event: dict)-> Dict[str, str | int]:
    return {
        'grand_prix' : session_data.session_info['Meeting']['Name'],
        'location' : session_data.session_info['Meeting']['Circuit']['ShortName'],
        'country_name' : session_data.session_info['Meeting']['Country']['Name'],
        'country_code' : session_data.session_info['Meeting']['Country']['Code'],
        'round_number' : event['RoundNumber'],
        'session' : session_data.session_info['Name'],
        'year' : session_data.session_info['StartDate'].year
    }
