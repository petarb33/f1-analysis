import pandas as pd
from fastf1.core import Session

def pick_quicklaps(session_data: Session, drivers: list[str]) -> dict[str, pd.DataFrame]:
    """
    Pick quick laps for each driver.

    Parameters
    ----------
    session_data : fastf1.core.Session
        FastF1 session object with session data.
    drivers : list of str
        List of drivers (driver abbreviation) whose laps will be picked.

    Returns
    -------
    dict
        Dictionary mapping driver to DataFrame of quick laps.
    """
    laps = {drv:pd.DataFrame() for drv in drivers}

    for driver in drivers:
        quick_laps = session_data.laps.pick_drivers(driver).pick_wo_box().pick_quicklaps()
        quick_laps['LapTime (s)'] = quick_laps['LapTime'].dt.total_seconds()
        laps[driver] = quick_laps.reset_index(drop=True)
    
    return laps


def pick_racelaps(session_data: Session, drivers: list[str]) -> dict[str, pd.DataFrame]:
    """
    Pick race laps for each driver, filtering out box laps,
    safety car, and VSC laps. Also fills missing lap times.

    Args:
    session_data : fastf1.core.Session
        FastF1 session object with session data.
    drivers : list of str
        List of drivers (driver abbreviation) whose laps will be picked.

    Returns:
        Dictionary mapping driver to DataFrame of race laps.
    """
    laps = {drv:pd.DataFrame() for drv in drivers}

    for driver in drivers:
        race_laps = session_data.laps.pick_drivers(driver).pick_wo_box()
        race_laps['LapTime (s)'] = race_laps['LapTime'].dt.total_seconds()

        race_laps = race_laps[
            ~race_laps['TrackStatus'].str.contains(r'[4567]', na=False)
        ]

        race_laps = fill_missing_laps(race_laps)
        laps[driver] = race_laps.reset_index(drop=True)

    return laps


def fill_missing_laps(laps) -> pd.DataFrame:
    """
    Fill missing lap times from sector times if all sectors are valid.

    Parameters
    ----------
        laps: DataFrame of laps.

    Returns
    -------
        DataFrame with missing LapTime (s) filled where possible.
    """
    for index, lap in laps.iterrows():
        if pd.isna(lap['LapTime']):
            s1, s2, s3 = lap['Sector1Time'], lap['Sector2Time'], lap['Sector3Time']
            if all(pd.notna(sector) for sector in (s1, s2, s3)):
                laptime = s1.total_seconds() + s2.total_seconds() + s3.total_seconds()
                laps.at[index, 'LapTime (s)'] = laptime
                print(
                    f'At Lap {lap['LapNumber']} for {lap['Driver']}'
                    f'changed NaN to {laptime:.3f}'
                )

    return laps


def create_stints(laps: dict[str, pd.DataFrame]) -> dict[str, dict[int, pd.DataFrame]]:
    """
    Create stints (groups of laps per driver and stint number).

    Parameters
    ----------
    laps : pd.DataFrame
        Dictionary mapping driver to laps DataFrame.

    Returns
    -------
        Dictionary of driver to {stint_number -> laps DataFrame}.
    """
    stints = {}

    for driver, driver_laps in laps.items():
        driver_stints = {}

        for _, lap in driver_laps.iterrows():
            stint_number = lap['Stint']
            driver_stints.setdefault(stint_number, []).append(lap)

        stints[driver] = {
            stint: pd.DataFrame(lap_list)
            for stint, lap_list in driver_stints.items()
        }

    return stints