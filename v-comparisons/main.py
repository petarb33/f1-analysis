from fetch import get_input, get_data, get_drivers, get_event_info
from process import get_drivers_speeds
from plot import plot_speed_comparisons

def main():
    country, year, session = get_input()

    session_data, event = get_data(country, year, session)

    drivers = get_drivers(session_data)

    event_info = get_event_info(session_data, event)

    min_speeds, mean_speeds, max_speeds = get_drivers_speeds(
        session_data, drivers
    )

    plot_speed_comparisons(
        session_data, min_speeds, mean_speeds, max_speeds, event_info
    )


if __name__ == "__main__":
    main()