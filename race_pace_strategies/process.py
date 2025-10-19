import pandas as pd
from fastf1.core import Session

def get_laps(race_data: Session) -> list[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Extract, clean, and transform race laps data.

    Parameters
    ----------
    race_data : Session
        Session object containing `.laps` (with method `pick_wo_box`) and `.results`.

    Returns
    -------
    transformed_laps : pd.DataFrame
        Cleaned laps DataFrame with a numeric column 'LapTime (s)'.
    drivers_order : pd.Index
        Driver names ordered by ascending mean lap time.
    drivers_mean_laptimes : pd.DataFrame
        DataFrame with columns ['Driver', 'LapTime (s)'] containing mean lap times,
        rounded to 3 decimals and sorted ascending by time.
    """
    laps = race_data.laps.pick_wo_box().copy()

    race_results = race_data.results['ClassifiedPosition']
    race_results = race_results[
        race_results.apply(lambda x: x not in {'R', 'W', 'N', 'F', 'E', 'D'})
    ]

    transformed_laps = laps.copy()
    transformed_laps['LapTime (s)'] = laps['LapTime'].dt.total_seconds()

    transformed_laps = fill_missing_laps(transformed_laps)

    transformed_laps = transformed_laps[
        ~transformed_laps['TrackStatus'].str.contains(r'[4567]', na=False)
    ]
    transformed_laps = transformed_laps[
        transformed_laps['DriverNumber'].isin(race_results.index)
        & transformed_laps['LapTime (s)'].notna()
    ]

    drivers_order = (
        transformed_laps.groupby('Driver')['LapTime (s)']
        .mean()
        .sort_values()
        .index
    )

    drivers_mean_laptimes = (
        transformed_laps.groupby('Driver')['LapTime (s)']
        .mean()
        .round(3)
        .sort_values()
        .reset_index()
    )

    return transformed_laps, drivers_order, drivers_mean_laptimes

def fill_missing_laps(laps: pd.DataFrame) -> pd.DataFrame:
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
            if all(pd.notna([s1, s2, s3])):
                laptime = s1.total_seconds() + s2.total_seconds() + s3.total_seconds()
                laps.at[index, 'LapTime (s)'] = laptime
                print(
                    f"At Lap {lap['LapNumber']} for {lap['Driver']} "
                    f"changed NaN to {laptime:.3f}"
                )
    return laps

def get_stints(race_data: Session) -> pd.DataFrame:
    """
    Group laps by driver, stint, and compound to calculate stint lengths.

    This function extracts relevant columns from the session's laps data and groups
    them by `Driver`, `Stint`, and `Compound` to determine the length of each stint
    (i.e., the number of laps completed in that stint on that compound).

    Parameters
    ----------
    race_data : Session
        Session object containing:
        - `.laps` : pandas.DataFrame with lap information (must include columns
          'Driver', 'Stint', 'Compound', 'LapNumber').

    Returns
    -------
    stints : pandas.DataFrame
        DataFrame with one row per unique (Driver, Stint, Compound) and the
        following columns:
        - ``Driver`` : str - Driver abbreviation.
        - ``Stint`` : int - Stint number.
        - ``Compound`` : str - Tyre compound used during the stint.
        - ``StintLength`` : int - Number of laps in the stint.
    """
    stints = race_data.laps[['Driver','Stint','Compound','LapNumber']]
    
    stints = (
        stints.groupby(['Driver','Stint','Compound'])
        .count()
        .reset_index()
        .rename(columns={'LapNumber':'StintLength'})
    )

    return stints