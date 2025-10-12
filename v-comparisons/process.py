import pandas as pd

def get_driver_speed_column(session_data, driver):
    """Helper function to extract speed data for the fastest lap of a driver."""
    fastest_lap = session_data.laps.pick_drivers(driver).pick_fastest()
    if fastest_lap is None:
        return  pd.Series(dtype='float64')
        # return empty Series to avoid breaking later
    return fastest_lap.get_car_data()['Speed']

def get_drivers_min_speeds(session_data):
    """Returns a DataFrame of minimum speeds for each driver."""
    drivers = list(session_data.results['Abbreviation'])
    min_speeds = [
        {'Driver': driver, 'Speed': speed}
        for driver in drivers
        if not pd.isna(speed := get_driver_speed_column(session_data, driver).min())
    ]
    return pd.DataFrame(min_speeds).sort_values(by='Speed', ascending=False)

def get_drivers_mean_speeds(session_data):
    """Returns a DataFrame of mean speeds for each driver."""
    drivers = list(session_data.results['Abbreviation'])
    mean_speeds = [
        {'Driver': driver, 'Speed': speed}
        for driver in drivers
        if not pd.isna(speed := get_driver_speed_column(session_data, driver).mean())
    ]
    return pd.DataFrame(mean_speeds).sort_values(by='Speed', ascending=False)

def get_drivers_max_speeds(session_data):
    """Returns a DataFrame of maximum speeds for each driver."""
    drivers = list(session_data.results['Abbreviation'])
    max_speeds = [
        {'Driver': driver, 'Speed': speed}
        for driver in drivers
        if not pd.isna(speed := get_driver_speed_column(session_data, driver).max())
    ]
    return pd.DataFrame(max_speeds).sort_values(by='Speed', ascending=False)
