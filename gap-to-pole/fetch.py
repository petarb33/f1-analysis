import fastf1
import json
from fastf1.core import Session
from fastf1.events import Event
from typing import Tuple, Dict, List

def get_input() -> Tuple[str, int]:
    """"
    Load the session configuration and return the country and year.

    This function reads the session configuration from a local JSON file
    using `load_session` and extracts the `country` and `year` fields.

    Returns
    -------
    tuple of (str, int)
        A tuple containing:
        - country : str
            The name of the country for the race weekend.
        - year : int
            The year of the event.
    """
    config = load_session()
    return config['country'], config['year']

def load_session() -> Dict[str, int]:
    """
    Load the session configuration from a JSON file.
    
    Reads the 'session.json' file located in the current working directory,
    that contains 'country' and 'year' keys.

    Returns
    -------
    dict
        Dictionary containing session configuration values. Session value
        is not needed as this graph can only be performed on qualifying.
        - 'country' : str
            Race country names, alternative names also work (e.g., "Miami"),
            since there are multiple races in same countries (e.g, "United States").
        - 'year' : int
            Year of the race weekend
    """
    file_path = 'session.json'
    with open(file_path, 'r') as f:
        return json.load(f)

def get_data(country: str, year: int) -> Tuple[Session, Event]:
    """
    Fetch and load FastF1 session and event data for given input.

    This functions uses FastF1 Api to get Qualifying data and the corresponding
    event information.

    Parameters
    ----------
    country : str
        Name of the country where the race is held (e.g., "Monaco")
    year : int
        Year of the race weekend.

    Returns
    -------
    tuple of (Session, Event)
        A tuple containing:
        - session_data : fastf1.core.Session
            Loaded FastF1 session object.
        - event : fastf1.events.Event
            Event object.
    """
    session_data = fastf1.get_session(year, country, 'Qualifying')
    session_data.load()
    event = fastf1.get_event(year, country)

    return session_data, event

def get_event_info(session_data: Session, event: Event) -> Dict[str, str | int]:
    """
    Extract structured information about the race weekend.

    Parameters
    ----------
    session_data : fastf1.core.Session
        FastF1 session object with session information.
    event : fastf1.events.Event
        FastF1 event object with general race weekend information.

    Returns
    -------
    dict
        Dictionary with information about the whole weekend:
        - 'grand_prix' : str
            Official Grand Prix Name.
        - 'location' : str
            Circuit short name.
        - 'country_name' : str
            Name of the country.
        - 'country_code' : str
            ISO Country code.
        - 'round_number' : int
            Round number
        - 'session' : str
            Session type (e.q., 'Practice 1')
        - 'year' : int
            Year of the race weekend
    """
    return {
        'grand_prix' : session_data.session_info['Meeting']['Name'],
        'location' : session_data.session_info['Meeting']['Circuit']['ShortName'],
        'country_name' : session_data.session_info['Meeting']['Country']['Name'],
        'country_code' : session_data.session_info['Meeting']['Country']['Code'],
        'round_number' : event['RoundNumber'],
        'session' : session_data.session_info['Type'],
        'year' : session_data.session_info['StartDate'].year
    }

def get_drivers(session_data: Session) -> List[str]:
    """
    Retrieve a list of driver abbreviations from the session results.

    Parameters
    ----------
    session_data : fastf1.core.Session
        The FastF1 session object containing timing and classification data.

    Returns
    -------
    list of str
        A list of all driver abbreviations (e.g., ['VER', 'HAM', 'LEC']) 
        who participated in the given session.
    """
    return list(session_data.results['Abbreviation'])