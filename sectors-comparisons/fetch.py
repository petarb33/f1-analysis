import fastf1
import json

def get_input():
    """"
    Load the session configuration and return the country, year and session.

    This function reads the session configuration from a local JSON file
    using `load_session` and extracts the `country`, `year` and 'session' fields.

    Returns
    -------
    tuple of (str, int)
        A tuple containing:
        - country : str
            The name of the country for the race weekend.
        - year : int
            The year of the event.
        - session : str
            Session to load.
    """
    config = load_session()
    return config['country'], config['year'], config['session']


def load_session():
    """
    Load the session configuration from a JSON file.
    
    Reads the 'session.json' file located in the current working directory,
    that contains 'country', 'year' and 'session' keys.

    Returns
    -------
    dict
        Dictionary containing session configuration values.
        - 'country' : str
            Race country names, alternative names also work (e.g., "Miami"),
            since there are multiple races in same countries (e.g., "United States").
        - 'year' : int
            Year of the race weekend.
        - 'session' : str
            Specific session of the event to analyze (e.g., 'Practice 1') .
    """
    file_path = "session.json"
    with open(file_path, "r") as f:
        return json.load(f)


def get_data(country, year, session):
    """
    Fetch and load FastF1 session and event data for given input.

    This functions uses FastF1 Api to get specific session data
    and the corresponding event information.

    Parameters
    ----------
    country : str
        Name of the country where the race is held (e.g., "Monaco")
    year : int
        Year of the race weekend.
    session : str
        Specific session of the event to analyze (e.g., 'FP1')

    Returns
    -------
    tuple of (Session, Event)
        A tuple containing:
        - session_data : fastf1.core.Session
            Loaded FastF1 session object.
        - event : fastf1.events.Event
            Event object.
    """
    session_data = fastf1.get_session(year, country, session)
    session_data.load()
    event = fastf1.get_event(year, country)

    return session_data, event


def get_event_info(session_data, event):
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
        'session' : session_data.session_info['Name'],
        'year' : session_data.session_info['StartDate'].year
    }


def get_drivers(session_data):
    return list(session_data.results['Abbreviation'])



    