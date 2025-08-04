import pandas as pd


def get_fastest_lap_sectors(session, drivers):
    fastest_sectors = {
        'Sector1Time': {'Time': float('inf'), 'Driver': 'VER'},
        'Sector2Time': {'Time': float('inf'), 'Driver': 'VER'},
        'Sector3Time': {'Time': float('inf'), 'Driver': 'VER'}
    }

    for driver in drivers:
        fastest_lap = session.laps.pick_drivers(driver).pick_fastest()

        if fastest_lap.empty:
            continue

        for sector in fastest_sectors:
            time = fastest_lap[sector].total_seconds()
            if time < fastest_sectors[sector]['Time']:
                fastest_sectors[sector]['Time'] = time
                fastest_sectors[sector]['Driver'] = driver

    return fastest_sectors


def get_driver_deltas(session, drivers, fastest_sectors):
    sectors_data = {
        'Sector1Time': [],
        'Sector2Time': [],
        'Sector3Time': []
    }

    for driver in drivers:
        fastest_lap = session.laps.pick_drivers(driver).pick_fastest()

        if fastest_lap.empty:
            continue

        for sector in ['Sector1Time', 'Sector2Time', 'Sector3Time']:
            sector_time = fastest_lap[sector].total_seconds()
            fastest_time = fastest_sectors[sector]['Time']
            tyre = fastest_lap['Compound']
            delta = sector_time - fastest_time

            sectors_data[sector].append(
                {'Driver': driver, 'Time': sector_time, 'Delta': delta, 'Tyre':tyre}
            )

    sector_dfs = {}
    for sector, data in sectors_data.items():
        df = pd.DataFrame(data).sort_values(by='Time').reset_index(drop=True)
        sector_dfs[sector] = df
    
    return {i + 1: sector_dfs[sector] for i, sector in enumerate(sectors_data)}


def get_fastest_sectors(session_data, drivers):
    sectors_data = {
        'Sector1Time': [],
        'Sector2Time': [],
        'Sector3Time': []
    }
    
    fastest_s1 = session_data.laps['Sector1Time'].min().total_seconds()
    fastest_s2 = session_data.laps['Sector2Time'].min().total_seconds()
    fastest_s3 = session_data.laps['Sector3Time'].min().total_seconds()
    fastest_sectors = {'Sector1Time': fastest_s1, 'Sector2Time': fastest_s2, 'Sector3Time': fastest_s3}

    for driver in drivers:
        drivers_laps = session_data.laps.pick_drivers(driver)

        if drivers_laps.empty:
            continue

        for sector in ['Sector1Time', 'Sector2Time', 'Sector3Time']:
            if drivers_laps[sector].isna().all():
                continue
            
            sector_idx = drivers_laps[sector].idxmin()
            sector_time = drivers_laps[sector].min().total_seconds()
            sector_tyre = drivers_laps.at[sector_idx, 'Compound']
            delta = sector_time - fastest_sectors[sector]
            
            if pd.notna(sector_time):
                sectors_data[sector].append({
                    'Driver': driver,
                    'Time': sector_time,
                    'Delta': delta,
                    'Tyre': sector_tyre
                })

    sector_dfs = {}
    for sector, data in sectors_data.items():
        df = pd.DataFrame(data).sort_values(by='Time').reset_index(drop=True)
        sector_dfs[sector] = df
    
    return {i + 1: sector_dfs[sector] for i, sector in enumerate(sectors_data)}


def is_valid_time(time):
    return bool(time) and not pd.isna(time)


    
