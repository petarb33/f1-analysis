from fetch import get_data, get_event_info, get_input
from process import pick_quicklaps, create_stints, pick_racelaps
from plot import create_graph


def main():
    country, year, drivers = get_input()

    session_data, event = get_data(year, country)

    event_info = get_event_info(session_data, event)

    quick_laps = pick_quicklaps(session_data, drivers)

    race_laps = pick_racelaps(session_data, drivers)

    stints = create_stints(quick_laps)

    create_graph(drivers, stints, event_info, session_data)

if __name__ == '__main__':
    main()