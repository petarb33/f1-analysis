from fetch import get_input, get_data, get_drivers, get_event_info
from process import get_drivers_max_speeds, get_drivers_mean_speeds, get_drivers_min_speeds
from plot import plot_speed_comparisons

def main():
    country, year, session = get_input()

    session_data, event = get_data(country, year, session)

    drivers = get_drivers(session_data)

    event_info = get_event_info(session_data, event)

    min_speeds = get_drivers_min_speeds(session_data)
    max_speeds = get_drivers_max_speeds(session_data)
    mean_speeds = get_drivers_mean_speeds(session_data)

    plot_speed_comparisons(
        session_data, min_speeds, mean_speeds, max_speeds, event_info
    )


if __name__ == "__main__":
    main()