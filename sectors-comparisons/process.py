import pandas as pd

def get_fastest_sector_data(session, drivers) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    """
    Collect each driver's fastest sector times and corresponding deltas for a session.

    Parameters
    ----------
    session : fastf1.core.Session
        FastF1 session object containing session data.
    drivers : list of str
        List of driver abbreviations - drivers that participated in the session.

    Returns
    -------
    tuple
        A tuple (time_dict, delta_dict) where:
        - time_dict : dict
            Dictionary keyed by sector name ('Sector1Time', 'Sector2Time', 'Sector3Time').
            Sorted by 'Time'.
            Each value is a pandas.DataFrame with columns:
            Driver : str
                Driver abbreviation.
            Time : float
                Driver's fastest sector time in seconds.
            Compound : object
                Tyre compound used on the lap that produced the fastest sector.
            Delta : float
                Difference in seconds between the driver's fastest sector time
                and the session's fastest sector time (leader has Delta = 0.0).
        - delta_dict : dict
            Dictionary keyed by sector name ('Sector1Time', 'Sector2Time', 'Sector3Time').
            Sorted by 'Delta'.
            Each value is a pandas.DataFrame with columns:
            Driver : str
                Driver abbreviation.
            Time : float
                Driver's fastest sector time in seconds.
            Compound : object
                Tyre compound used on the lap that produced the fastest sector.
            Delta : float
                Difference in seconds between the driver's fastest sector time
                and the session's fastest sector time (leader has Delta = 0.0).
    """
    fastest_sectors = get_fastest_sectors(session)
    time_dict, delta_dict = {}, {}
    
    for sector in ['Sector1Time','Sector2Time','Sector3Time']:
        time_data_list = []
        for driver in drivers:
            time_data = get_driver_fastest_sector(session, driver, sector, fastest_sectors[sector])

            if time_data is not None:
                time_data_list.append(time_data)
    
        time_df = pd.DataFrame(time_data_list).sort_values(by='Time').reset_index(drop=True)
        delta_df = pd.DataFrame(time_data_list).sort_values(by='Delta').reset_index(drop=True)
        
        time_dict[sector] = time_df
        delta_dict[sector] = delta_df

    return time_dict, delta_dict

def get_fastest_sectors(session) -> dict[str, float]:
    """
    Returns fastest time for each sector, which will be used to calculate delta.

    Parameters
    ----------
    session : fastf1.core.Session
        FastF1 session object containing session data.
        The function reads sector times from session.laps and ignores missing values.
    
    Returns
    -------
    dict
        Keys: 'Sector1Time' (float, seconds), 'Sector2Time' (float, seconds), 'Sector3Time' (float, seconds)
        Description: Fastest sector time for each sector. 
    """
    laps = session.laps
    return {
        sector: laps[sector].dropna().min().total_seconds()
        for sector in ['Sector1Time', 'Sector2Time', 'Sector3Time']
    }

def get_driver_fastest_sector(session, driver, sector, fastest_sector_time) -> dict[str, str | float]:
    """
    Function returns drivers fastest sector time, delta to fastest
    sector and tyre on which sector is driven.

    Parameters
    ----------
    session : fastf1.core.Session
        FastF1 session object containing session data.
    driver : str
        Driver abbreviation for the driver which sector times are taken.
    sector : {'Sector1Time', 'Sector2Time', 'Sector3Time'}
        Which sector is taken.
    fastest_sector_time : float
        Fastest sector time for the given sector.
    
    Returns
    -------
    dict
        Keys: 'Driver' (str), 'Time' (float, seconds), 'Compound' (str)
        Description: the driver's fastest sector time and tyre compound for that lap.
    """
    laps = session.laps.pick_drivers(driver)

    sector_times = laps[sector].dropna()

    if sector_times.empty or fastest_sector_time is None:
        return None
    
    sector_time = sector_times.min().total_seconds()
    delta = sector_time - fastest_sector_time

    if sector_time > fastest_sector_time * 1.07:
        return None

    sector_idx = sector_times.idxmin()
    sector_compound = laps.at[sector_idx, 'Compound'] 

    return {'Driver': driver, 'Time': sector_time, 'Compound': sector_compound, 'Delta': delta}
    

def get_fastest_lap_sectors(session, drivers) -> dict[str, pd.DataFrame]:
    """
    Gather each driver's fastest-lap sector times and compute deltas to the sector leader.

    Parameters
    ----------
    session : fastf1.core.Session
        FastF1 session object containing session data.
    drivers : list of str
        List of driver abbreviations - drivers that participated in the session.

    Returns
    -------
    sectors_dict : dict
        Dictionary keyed by sector name ('Sector1Time', 'Sector2Time', 'Sector3Time').
        Each value is a pandas.DataFrame with four columns:
        Driver : str
            Driver abbreviation.
        Time : float
            Fastest sector time for that driver in seconds.
        Compound : object
            Tyre compound value taken from the driver's fastest lap (type depends on session data).
        Delta : float
            Difference in seconds between the driver's sector time and the sector leader
            (leader has Delta = 0.0).    
    """
    sectors = ['Sector1Time', 'Sector2Time', 'Sector3Time']
    sectors_dict = {sector: [] for sector in sectors}
    
    fastest_lap = session.laps.pick_fastest()
    slower_drivers = []

    for driver in drivers:
        drivers_fastest_lap = session.laps.pick_drivers(driver).pick_fastest()
        
        if (drivers_fastest_lap is None or
            pd.isna(drivers_fastest_lap['LapTime'])):
            print(f'LAPTIME FOR {driver} NOT SHOWN')
            continue

        if drivers_fastest_lap['LapTime'] > fastest_lap['LapTime'] * 1.07:
            slower_drivers.append(driver)

        for sector in sectors:
            sectors_dict[sector].append({
                'Driver': driver,
                'Time': drivers_fastest_lap[sector].total_seconds(),
                'Compound': drivers_fastest_lap['Compound']
            })

    for sector in sectors:
        df = pd.DataFrame(sectors_dict[sector]).sort_values(by='Time').reset_index(drop=True)

        if not df.empty:
            leader_time = df.loc[0, 'Time']
            df['Delta'] = df['Time'] - leader_time
        else:
            df['Delta'] = pd.Series(dtype='float64')
            
        sectors_dict[sector] = df

    quick_fl_sectors_dict = {}
    for sector in ['Sector1Time', 'Sector2Time', 'Sector3Time']:
        df = sectors_dict[sector]
        df = df[~df['Driver'].isin(slower_drivers)]
        quick_fl_sectors_dict[sector] = df

    return sectors_dict, quick_fl_sectors_dict

