import fastf1
import json

def get_input():
    config = load_session()
    return config['country'], config['year'], config['session']


def load_session():
    file_path = "session.json"
    with open(file_path, "r") as f:
        return json.load(f)


def get_data(country, year, session):
    session_data = fastf1.get_session(year, country, session)
    session_data.load()
    event = fastf1.get_event(year, country)

    return session_data, event


def get_event_info(session_data, event):
    return {
        'grand_prix': session_data.session_info['Meeting']['Name'],
        'location': session_data.session_info['Meeting']['Circuit']['ShortName'],
        'country_name': session_data.session_info['Meeting']['Country']['Name'],
        'country_code': session_data.session_info['Meeting']['Country']['Code'],
        'round_number': event['RoundNumber'],
        'session': session_data.session_info['Name'],
        'year': session_data.session_info['StartDate'].year
    }


def get_drivers(session_data):
    return list(session_data.results['Abbreviation'])
