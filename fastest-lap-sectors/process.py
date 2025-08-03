import pandas as pd


def get_fastest_sectors(session, drivers):
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


def is_valid_time(time):
    return bool(time) and not pd.isna(time)


    
