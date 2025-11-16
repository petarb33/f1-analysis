from fetch import get_input, get_data, get_event_info
from process import get_lap
from plot import create_graph

def main():
    country, session_name, year, driver1, driver2, lap1, lap2 = get_input()
    session_data, event = get_data(country, year, session_name)
    event_info = get_event_info(session_data, event)
 
    car_data = {}
    car_data = get_lap(session_data, driver1, lap1, car_data)
    car_data = get_lap(session_data, driver2, lap2, car_data)
    create_graph(car_data, session_data, event_info)

if __name__ == "__main__":
    main()