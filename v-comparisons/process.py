import pandas as pd


def get_drivers_speeds(session_data, drivers):
    max_speeds = []
    min_speeds = []
    mean_speeds = []

    for driver in drivers:
        speed_column = (
            session_data.laps
            .pick_drivers(driver)
            .pick_fastest()
            .get_car_data()['Speed']
        )

        max_speeds.append({'Driver': driver, 'Speed': speed_column.max()})
        min_speeds.append({'Driver': driver, 'Speed': speed_column.min()})
        mean_speeds.append({'Driver': driver, 'Speed': round(speed_column.mean(), 1)})

    max_speeds = pd.DataFrame(max_speeds).sort_values(by='Speed', ascending=False)
    min_speeds = pd.DataFrame(min_speeds).sort_values(by='Speed', ascending=False)
    mean_speeds = pd.DataFrame(mean_speeds).sort_values(by='Speed', ascending=False)

    return min_speeds, mean_speeds, max_speeds
