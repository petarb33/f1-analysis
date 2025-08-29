import pandas as pd
from fastf1.core import Session

def get_laps(race_data: Session) -> list[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Extract, clean and transform race laps data"""
    laps = race_data.laps.pick_wo_box()

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
    """Fill missing lap times using sector times if possible"""
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
    """Return a DataFrame with stint information for each driver."""
    stints = race_data.laps[['Driver','Stint','Compound','LapNumber']]
    
    stints = (
        stints.groupby(['Driver','Stint','Compound'])
        .count()
        .reset_index()
        .rename(columns={'LapNumber':'StintLength'})
    )

    return stints