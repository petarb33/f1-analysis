from fetch import get_data, get_input, get_event_info, get_drivers
from process import get_fastest_lap_sectors, get_driver_deltas, get_fastest_sectors
from plot import create_graph, plot_sectors_delta, plot_sectors_time


def main():
    country, year, session = get_input()

    session_data, event = get_data(country, year, session)
    event_info = get_event_info(session_data, event)
    drivers = get_drivers(session_data)

    fastest_lap_sectors = get_fastest_lap_sectors(session_data, drivers)
    fl_sectors_dict = get_driver_deltas(session_data, drivers, fastest_lap_sectors)
    fastest_sectors_dict = get_fastest_sectors(session_data, drivers)

    create_graph(
        session_data,
        fl_sectors_dict,
        event_info,
        plot_func=plot_sectors_time,
        title='Fastest Lap in Sectors - Sector Time',
        label='fl_sectors',
    )
    create_graph(
        session_data,
        fl_sectors_dict,
        event_info,
        plot_func=plot_sectors_delta,
        title='Fastest Lap in Sectors - Time Delta',
        label='fl_sectors_delta',
    )
    create_graph(
        session_data,
        fastest_sectors_dict,
        event_info,
        plot_func=plot_sectors_time,
        title='Fastest Sectors - Sector Time',
        label='fastest_sectors',
    )
    create_graph(
        session_data,
        fastest_sectors_dict,
        event_info,
        plot_func=plot_sectors_delta,
        title='Fastest Sectors - Time Delta',
        label='fastest_sectors_delta',
    )


if __name__ == "__main__":
    main()
