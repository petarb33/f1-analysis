import pandas as pd
from typing import List
from fastf1.core import Session

def extract_quali_laps(session_data: Session, drivers: List) -> pd.DataFrame:
    """
    Extract qualifying lap data from a given session (Qualifying or Sprint Qualifying).

    Returns a DataFrame with the lap time that secured each driver's final grid position,
    the qualifying phase in which the lap was set (Q1/Q2/Q3), and the time gap to pole.

    Parameters
    ----------
    session_data : fastf1.core.Session
        The FastF1 session object containing qualifying session data.
    drivers : list of str
        List of driver abbreviations to include in the result.

    Returns
    -------
    pandas.DataFrame
        Columns:
        - 'Driver' : str
        - 'LapTime' : float (seconds)
        - 'Session' : str ('Q1', 'Q2', 'Q3')
        - 'GapToPole' : float (seconds)
    """

    quali_data = []
    pole_laptime = session_data.results.iloc[0]['Q3'].total_seconds()
    
    for row in session_data.results.itertuples():
        if row.Abbreviation not in drivers:
            continue


        for phase in ['Q3', 'Q2', 'Q1']:

            time = getattr(row, phase)
            if not pd.isna(time):
                laptime = pd.Timedelta(time).total_seconds
                quali_data.append({
                    'Driver': row.Abbreviation,
                    'LapTime': laptime,
                    'Session': phase,
                    'GapToPole': round(laptime - pole_laptime, 3)
                })

    return pd.DataFrame(quali_data)



