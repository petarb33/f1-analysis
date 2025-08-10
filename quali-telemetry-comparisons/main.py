from data_fetching import get_data, get_event_info, get_input, get_drivers
from data_processing import get_quali_laps_car_data, get_quali_laps
from plotting import create_full_graphs, create_delta_graphs

def main():
    country, year, drivers = get_input()
    
    session_data, event = get_data(country, year)

    event_info = get_event_info(session_data, event)

    sorted_drivers = get_drivers(session_data, drivers)

    drivers_laptimes = get_quali_laps(session_data, sorted_drivers)

    car_data = get_quali_laps_car_data(session_data, drivers_laptimes)

    create_full_graphs(session_data, car_data, event_info)

    create_delta_graphs(session_data, car_data, event_info)


if __name__ == "__main__":
    main()