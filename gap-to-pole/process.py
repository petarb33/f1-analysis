import pandas as pd
from typing import List
from fastf1.core import Session

def get_quali_data(session_data: Session, drivers: List) -> pd.DataFrame:
    """
    Extract qualifying lap data from a given session (Qualifying or Sprint Qualifying).

    This function returns a DataFrame containing the lap time that secured each driver's 
    final grid position, the qualifying phase in which the lap was set (Q1/Q2/Q3), and 
    the time gap to the pole position lap.

    Note: This function does NOT return each driver's fastest lap in qualifying, 
    but rather the lap that determined their final grid position.

    Example:
    If LEC (Charles Leclerc) sets a 1:15.000 in Q2, but later sets a slower 1:16.000 
    in Q3 and qualifies P3, then the Q3 lap (1:16.000) will be taken — because that 
    is the lap that earned him that grid spot.

    Parameters:
        session_data (Session): FastF1 session object containing session information.
        drivers (List[str]): List of driver abbreviations to include in the result.

    Returns:
        pd.DataFrame: DataFrame with the following columns:
            - Driver (str): Driver abbreviation.
            - LapTime (float): Best lap time in seconds.
            - Session (str): Qualifying phase in which the time was set (Q1/Q2/Q3).
            - GapToPole (float): Time difference to the pole lap in seconds.
    """
    quali_data = []

    pole_laptime = session_data.results.iloc[0]['Q3'].total_seconds()
    for row in session_data.results.itertuples():
        abbreviation = row.Abbreviation
        if abbreviation not in drivers:
            continue

        q_times = [row.Q1, row.Q2, row.Q3]
        phases = ['Q1', 'Q2', 'Q3']

        laptime = None
        quali_phase = 'NoTime'

        for time, phase in zip(q_times, phases):
            if not pd.isna(time):
                laptime = pd.Timedelta(time).total_seconds()
                quali_phase = phase

        if laptime is not None:
            delta = round(laptime - pole_laptime, 3)
            quali_data.append({
                'Driver': abbreviation,
                'LapTime': laptime,
                'Session': quali_phase,
                'GapToPole': delta
            })

    quali_data_df = pd.DataFrame(quali_data)
    
    return quali_data_df


