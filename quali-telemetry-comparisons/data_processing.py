import pandas as pd
from fastf1.core import Session
from f1_types import CarDataEntry, QualiLapsEntry

def get_quali_laps_car_data(session_data: Session, drivers_laptimes: QualiLapsEntry) -> CarDataEntry:
    car_data = {}

    for drv, value in drivers_laptimes.items():
        laptime = value['laptime']
        quali_phase = value['quali_phase']
        position = value['position']
        laps = session_data.laps.pick_drivers(drv)
        for _, lap in laps.iterrows():
            if lap['LapTime'].total_seconds() == laptime:
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
    minutes = int(seconds // 60)
    sec = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{minutes}:{sec:02}:{millis:03}"