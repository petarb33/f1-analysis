import pandas as pd

def get_lap(session_data, driver, lap_input, car_data):
    """
    Retrieve lap information and telemetry for a specific driver and lap.

    Parameters
    ----------
    session_data : fastf1.core.Session
        Session object containing full session data, including laps and telemetry.
    driver : str
        Driver identifier (e.g., "VER", "HAM") used to filter laps.
    lap_input : int or str
        Lap selector. If an `int`, selects a lap by lap number.
        If a `str`, it should represent a lap time in the format ``"mm:ss.sss"``.
    car_data : dict
        Dictionary that will be updated with extracted lap information for the driver.
        The function adds/overwrites the entry ``car_data[driver]``.

    Returns
    -------
    dict
        The updated `car_data` dictionary, containing for the given driver:
        - ``'laptime'`` : pandas.Timedelta  
            The lap time of the selected lap.
        - ``'lap_number'`` : int  
            The lap number associated with the selected lap.
        - ``'telemetry'`` : pandas.DataFrame  
            Telemetry data for that lap, enriched with distance via ``add_distance()``.

    Raises
    ------
    ValueError
        If `lap_input` is a string with an invalid format, or no lap matches the given time.
    TypeError
        If `lap_input` is neither an integer nor a string.

    Notes
    -----
    When selecting laps by time string, the function expects the format
    ``"mm:ss.sss"`` and internally prepends ``"00:"`` before parsing
    (e.g., ``"1:23.456" → "00:1:23.456"``).
    """
    laps = session_data.laps.pick_drivers(driver)
    lap = None
    lap_number = None
    laptime = None

    if isinstance(lap_input, int):
        lap = laps.pick_laps(lap_input)
        lap_number = lap_input
        laptime = lap['LapTime'].iloc[0].total_seconds()

    elif isinstance(lap_input, str):
        try:
            lap_time = pd.to_timedelta("00:" + lap_input)
        except Exception:
            raise ValueError(f"Invalid lap time format: {lap_input} or lap time doesn't exist.")

        lap = laps.loc[laps['LapTime'] == lap_time]

        if lap.empty:
            raise ValueError(f"No lap found matching time {lap_input} for driver {driver}")

        lap_number = int(lap.iloc[0]['LapNumber'])
        laptime = lap['LapTime'].iloc[0].total_seconds()

    else:
        raise TypeError("lap_input must be int (lap number) or str (lap time)")
    
    car_data[driver] = {
        'lap_object': lap,
        'laptime': format_laptime(laptime),
        'lap_number': lap_number,
        'telemetry': lap.get_car_data().add_distance()
    }

    return car_data

def format_laptime(seconds):
    """
    Parameters
    ----------
    seconds : float
        Laptime in seconds
    
    Returns
    -------
    str
        Formatted laptime, in format 'm:ss.MMM'
    """
    minutes = int(seconds // 60)
    sec = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{minutes}:{sec:02}:{millis:03}"