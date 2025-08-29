from fetch import get_data, get_event_info, get_input, get_drivers
from process import get_laps, get_stints
from plot import create_multi_graph, get_drivers_colors, create_pace_graph, create_stints_graph

def main():
    country, year = get_input()

    race_data, event = get_data(country, year)

    event_info = get_event_info(race_data, event)

    drivers = get_drivers(race_data)

    laps, drivers_order, drivers_mean_laptimes = get_laps(race_data)

    stints = get_stints(race_data)

    drivers_colors = get_drivers_colors(race_data)

    create_multi_graph(
        race_data,
        laps,
        stints,
        drivers_order,
        drivers_colors,
        drivers,
        event_info
    )

    create_pace_graph(
        laps,
        drivers_order,
        drivers_colors,
        event_info
    )

    create_stints_graph(
        race_data,
        stints,
        drivers,
        event_info
    )

if __name__ == "__main__":
    main()