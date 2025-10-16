from fetch import get_data, get_input, get_event_info, get_drivers
from process import get_fastest_sector_data, get_fastest_lap_sectors
from plot import create_graph, plot_sectors_time


def main():
    country, year, session = get_input()

    session_data, event = get_data(country, year, session)
    event_info = get_event_info(session_data, event)
    drivers = get_drivers(session_data)

    time_dict, delta_dict = get_fastest_sector_data(session_data, drivers)

    create_graph(
        session_data,
        time_dict,
        event_info,
        title='Fastest Sectors',
        label='fastest_sectors',
    )

    create_graph(
        session_data,
        delta_dict,
        event_info,
        title='Fastest Sectors - Delta',
        label='fastest_sectors_delta',
        mode='Delta'
    )

    fastest_lap_sectors = get_fastest_lap_sectors(session_data, drivers)

    create_graph(
        session_data,
        fastest_lap_sectors,
        event_info,
        title='Fastest Lap in Sectors',
        label='fl_sectors',
    )

    create_graph(
        session_data,
        fastest_lap_sectors,
        event_info,
        title='Fastest Lap in Sectors - Delta',
        label='fl_sectors_delta',
        mode='Delta'
    )

if __name__ == "__main__":
    main()
