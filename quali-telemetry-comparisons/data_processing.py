import pandas as pd
from fastf1.core import Session
from f1_types import CarDataEntry, QualiLapsEntry

def get_quali_laps_car_data(session_data: Session, drivers_laptimes: QualiLapsEntry) -> CarDataEntry:
    """
    Find and extract qualifying lap data for each driver based on their lap times.

    This function locates each driver's qualifying lap (from `drivers_laptimes`) 
    within the session data and returns a structured dictionary containing the 
    corresponding lap object, telemetry data, and metadata useful for telemetry plots.

    Parameters
    ----------
    session_data : fastf1.core.Session
        FastF1 session object containing session data.
    drivers_laptimes : dict[str, dict[str, Union[float, str, int]]]
        Dictionary with drivers laptimes, qualifying session and position.
    
    Returns
    -------
    dict[str, dict[str, Union[pd.DataFrame, str, lap, str, int]]]
        A dictionary mapping driver abbreviations to their qualifying lap data.
        Each value is a dictionary containing:

        - 'telemetry' (pd.DataFrame): Telemetry data used for telemetry line plots.
        - 'quali_phase' (str): The qualifying phase in which the lap was set 
          ('Q1', 'Q2', 'Q3', or 'NoTime').
        - 'lap' (fastf1.core.Lap): Lap object used for delta comparison plots.
        - 'laptime' (str): Lap time formatted as 'm:ss.MMM'.
        - 'position' (int): Driver's final qualifying position on the grid.

    """
    car_data = {}

    for drv, value in drivers_laptimes.items():
        laptime = value['laptime']
        quali_phase = value['quali_phase']
        position = value['position']
        laps = session_data.laps.pick_drivers(drv)
        for _, lap in laps.iterrows():
            if lap['LapTime'].total_seconds() == laptime:
                print(type(lap))
                car_data[drv] = {
                    'telemetry':lap.get_car_data().add_distance(),
                    'quali_phase':quali_phase,
                    'lap':lap,
                    'laptime':format_laptime(lap['LapTime'].total_seconds()),
                    'position':position
                }
                break

    return car_data

def get_quali_laps(session_data: Session, drivers: list) -> QualiLapsEntry:
    """
    Retrieve each driver's fastest qualifying lap that determined their grid position.

    If a driver did not set a lap time in a later qualifying phase (e.g., Q3), 
    their best lap from the previous session (e.g., Q2 or Q1) is used instead.

    Parameters
    ----------
    session_data : fastf1.core.Session
        FastF1 session object containing session data.
    drivers : list[str]
        List of driver abbreviations for which to retrieve lap times.

    Returns
    -------
    dict[str, dict[str, Union[float, str, int]]]
        A dictionary mapping driver abbreviations to their qualifying lap data.
        Each value is a dictionary containing:

        - 'laptime' (float): Lap time in seconds.
        - 'quali_phase' (str): The qualifying phase in which the lap was set 
        ('Q1', 'Q2', 'Q3', or 'NoTime').
        - 'position' (int): Final qualifying position on the grid.
    """
    drivers_quali_times = {drv: {
        'laptime': 0.0,
        'quali_phase': '',
        'position': 0
    } for drv in drivers}
    
    phases = ['Q1', 'Q2', 'Q3']
    for row in session_data.results.itertuples():
        driver = row.Abbreviation
        if driver not in drivers:
            continue

        q_times = [row.Q1, row.Q2, row.Q3]
        laptime = None
        quali_phase = 'NoTime'

        for q_time, phase in zip(q_times, phases):
            if not pd.isna(q_time):
                laptime = pd.Timedelta(q_time).total_seconds()
                quali_phase = phase

        drivers_quali_times[driver]['laptime'] = laptime
        drivers_quali_times[driver]['quali_phase'] = quali_phase
        drivers_quali_times[driver]['position'] = int(row.Position) 
        
    drivers_quali_times = {
        drv: (value if value is not None else tuple([0, 'NoTime' , 0]))
        for drv, value in drivers_quali_times.items()
    }

    return drivers_quali_times

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