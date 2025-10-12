import pandas as pd

def get_driver_speed_column(session_data, driver):
    """
    Return the Speed series for the driver's fastest lap.

    Parameters
    ----------
    session_data : fastf1.core.Session
        Object containing session data. Must call use pick_drivers(driver).pick_fastest()
        on session_data.laps to get fastest lap, and then use
        .get_car_data() to get the 'Speed' column of fastest lap
    driver : str
        Driver identifier (abbreviation) used to pick the driver's laps.

    Returns
    -------
    pandas.Series
        Series of speed values from the driver's fastest lap. Returns an empty
        float64 Series if no fastest lap is found.
    """

    fastest_lap = session_data.laps.pick_drivers(driver).pick_fastest()
    if fastest_lap is None:
        return  pd.Series(dtype='float64')
        # return empty Series to avoid breaking later
    return fastest_lap.get_car_data()['Speed']

def get_drivers_min_speeds(session_data):
    """
    Calculate the minimum speed reached by each driver on their fastest lap.

    This function extracts all drivers from the session results and uses 
    `get_driver_speed_column` to obtain their speed trace. For each driver, 
    it identifies the **minimum speed value** recorded on their fastest lap. 
    Drivers without valid speed data are excluded.

    Parameters
    ----------
    session_data : fastf1.core.Session
        Session object containing telemetry and results data.
        The 'Abbreviation' column from `session_data.results` is used to 
        determine the list of participating drivers.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with columns:
        - 'Driver': Driver abbreviation.
        - 'Speed' : Minimum speed (in km/h) recorded on their fastest lap.
        
        The DataFrame is sorted in descending order by 'Speed'.
    """

    drivers = list(session_data.results['Abbreviation'])
    min_speeds = [
        {'Driver': driver, 'Speed': speed}
        for driver in drivers
        if not pd.isna(speed := get_driver_speed_column(session_data, driver).min())
    ]
    return pd.DataFrame(min_speeds).sort_values(by='Speed', ascending=False)

def get_drivers_mean_speeds(session_data):
    """
    Calculate the mean speed by each driver on their fastest lap.

    This function extracts all drivers from the session results and uses 
    `get_driver_speed_column` to obtain their speed trace. For each driver, 
    it identifies the **mean speed value** on their fastest lap. 
    Drivers without valid speed data are excluded.

    Parameters
    ----------
    session_data : fastf1.core.Session
        Session object containing telemetry and results data.
        The 'Abbreviation' column from `session_data.results` is used to 
        determine the list of participating drivers.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with columns:
        - 'Driver': Driver abbreviation.
        - 'Speed' : Mean speed (in km/h) on their fastest lap.
        
        The DataFrame is sorted in descending order by 'Speed'.
    """
    drivers = list(session_data.results['Abbreviation'])
    mean_speeds = [
        {'Driver': driver, 'Speed': speed}
        for driver in drivers
        if not pd.isna(speed := get_driver_speed_column(session_data, driver).mean())
    ]
    return pd.DataFrame(mean_speeds).sort_values(by='Speed', ascending=False)

def get_drivers_max_speeds(session_data):
    """
    Calculate the max speed reached by each driver on their fastest lap.

    This function extracts all drivers from the session results and uses 
    `get_driver_speed_column` to obtain their speed trace. For each driver, 
    it identifies the **max speed value** reached on their fastest lap. 
    Drivers without valid speed data are excluded.

    Parameters
    ----------
    session_data : fastf1.core.Session
        Session object containing telemetry and results data.
        The 'Abbreviation' column from `session_data.results` is used to 
        determine the list of participating drivers.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with columns:
        - 'Driver': Driver abbreviation.
        - 'Speed' : Max speed (in km/h) on their fastest lap.
        
        The DataFrame is sorted in descending order by 'Speed'.
    """
    drivers = list(session_data.results['Abbreviation'])
    max_speeds = [
        {'Driver': driver, 'Speed': speed}
        for driver in drivers
        if not pd.isna(speed := get_driver_speed_column(session_data, driver).max())
    ]
    return pd.DataFrame(max_speeds).sort_values(by='Speed', ascending=False)
