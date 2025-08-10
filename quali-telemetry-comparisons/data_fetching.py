import fastf1
import json
from fastf1.core import Session
from fastf1.events import Event
from typing import Tuple, List, Dict
from f1_types import SessionConfig

def get_input() -> Tuple[str, int, List[str]]:
    """Load the session config and return country and year"""
    config = load_session()
    return config['country'], config['year'], config['drivers'].split()

def load_session() -> SessionConfig:
    """Load the session configuration from a JSON file."""
    file_path = 'session.json'
    with open(file_path, 'r') as f:
        return json.load(f)

def get_data(country: str, year: int) -> Tuple[Session, Event]:
    """Fetch the FastF1 session and event data."""
    session_data = fastf1.get_session(year, country, 'Q')
    session_data.load()
    event = fastf1.get_event(year, country)

    return session_data, event

def get_event_info(session_data: Session, event: Event) -> Dict[str, str | int]:
    return {
        'grand_prix' : session_data.session_info['Meeting']['Name'],
        'location' : session_data.session_info['Meeting']['Circuit']['ShortName'],
        'country_name' : session_data.session_info['Meeting']['Country']['Name'],
        'country_code' : session_data.session_info['Meeting']['Country']['Code'],
        'round_number' : event['RoundNumber'],
        'session' : session_data.session_info['Type'],
        'year' : session_data.session_info['StartDate'].year
        }

def get_drivers(session_data: Session, selected_drivers: list) -> List[str]:
    return [drv for drv in session_data.results['Abbreviation'] if drv in selected_drivers]
