from fetch import get_data, get_event_info, get_input, get_drivers
from process import get_quali_data
from plot import create_graph

def main():
    country, year = get_input()

    session_data, event = get_data(country, year)

    event_info = get_event_info(session_data, event)

    drivers = get_drivers(session_data)

    quali_data = get_quali_data(session_data, drivers)

    create_graph(quali_data, event_info, fig_width=10)

if __name__ == "__main__":
    main()