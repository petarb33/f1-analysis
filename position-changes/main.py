from fetch import get_input, get_event_info, get_data
from plot import create_graph


def main():
    country, year = get_input()
    session_data, event = get_data(country, year)
    event_info = get_event_info(session_data, event)

    create_graph(session_data, event_info)
    
    
if __name__ == "__main__":
    main()