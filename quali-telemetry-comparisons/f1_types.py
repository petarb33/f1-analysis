from typing import TypedDict
from fastf1.core import Telemetry, Lap

class CarDataEntry(TypedDict):
    telemetry: Telemetry
    quali_phase: str
    lap: Lap
    laptime: str
    position: int

class SessionConfig(TypedDict):
    country: str
    year: int
    drivers: str

class QualiLapsEntry(TypedDict):
    laptime: float
    quali_phase: str
    position: int