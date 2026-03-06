# F1 Analysis :checkered_flag:
![Python](https://img.shields.io/badge/python-3.12+-blue)
![FastF1](https://img.shields.io/badge/FastF1-api-red)
![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557c?logo=python&logoColor=white)
![Seaborn](https://img.shields.io/badge/Seaborn-4c72b0?logoColor=white)


---

A Python-based data analysis project focused on **Formula 1** data using the **FastF1 API**.

FastF1 is a python package for accessing and analyzing Formula 1 results, schedules, timing data and telemetry.

## :pushpin: Overview
This repository contains multiple analysis modules dedicated to exploring and getting better understanding of F1 sessions.
Using FastF1 API, project retrieves official F1 session data and applies data analysis to:

+ Study position changes throughout races
+ Compare lap telemetries
+ Analyze qualifying performance
+ Compare multiple drivers race laptimes
+ Compare sector times
+ Compare max, min and mean speed
+ Analyze overall race pace and strategies

## :toolbox: Tech Stack
+ **Python**
+ **FastF1 API**
+ **Pandas**
+ **Matplotlib / Seaborn**

## :file_folder: Project Structure

```
f1-analysis/
│
├── assets/
├── gap-to-pole/
├── input-examples/
├── lap-telemetry-comparison/
├── laps_comparisons/
├── position-changes/
├── quali-telemetry-comparisons/
├── race_pace_strategies/
├── sectors-comparisons/
├── v-comparisons/
├── README.md
└── colors.py
```

## :gear: Installation
> **Requires Python 3.12+**
```
git clone https://github.com/petarb33/f1-analysis.git
cd f1-analysis
pip install fastf1 pandas matplotlib seaborn
```

## :rocket: Usage
Each module is independent. Navigate to the desired folder and run:
```bash
cd gap-to-pole
python main.py
```
Configure the input by creating/copying `session.json` inside the folder (use the examples from `input-examples/` as a reference).

Results of scripts are images (.png) created in local `_output_plots/` folder.

## :bar_chart: Examples (Outputs)
### 1. Gap to Pole
![Gap to Pole](https://raw.githubusercontent.com/petarb33/f1-analysis/master/assets/qat_sprint_qualifying_gap_to_pole_10x10.png)

### 2. Lap Telemetry Comparison
![Lap Telemetry Comparison](https://raw.githubusercontent.com/petarb33/f1-analysis/master/assets/uae_race_VERvsNOR_lap55-54.png)
### 3. Laps Comparisons
![Laps Comparisons](https://raw.githubusercontent.com/petarb33/f1-analysis/master/assets/uae_NORvsPIA.png)
![Laps Comparisons](https://raw.githubusercontent.com/petarb33/f1-analysis/master/assets/uae_VERvsNORvsPIAvsLEC.png)

### 4. Position Changes
![Position Changes](https://raw.githubusercontent.com/petarb33/f1-analysis/master/assets/qat_race_position_changes.png)

### 5. Qualifying Telemetry Comparisons
![Qualifying Telemetry Comparisons](https://raw.githubusercontent.com/petarb33/f1-analysis/master/assets/uae_qualifying_VERvsNOR.png)
![Qualifying Telemetry Comparisons](https://raw.githubusercontent.com/petarb33/f1-analysis/master/assets/uae_qualifying_delta_VERvsNOR.png)

### 6. Race Pace & Strategies
![Strategies](https://raw.githubusercontent.com/petarb33/f1-analysis/master/assets/uae_strategies.png)
![Race Pace + Strategies](https://raw.githubusercontent.com/petarb33/f1-analysis/master/assets/uae_race_pace_strategies.png)
![Race Pace](https://raw.githubusercontent.com/petarb33/f1-analysis/master/assets/uae_race_pace.png)

### 7. Sector Time Comparisons
![Fastest Sectors](https://raw.githubusercontent.com/petarb33/f1-analysis/master/assets/uae_practice_3_fastest_sectors.png)
![Fastest Sectors Delta](https://raw.githubusercontent.com/petarb33/f1-analysis/master/assets/uae_practice_3_fastest_sectors_delta.png)
![Fastest Lap in Sectors](https://raw.githubusercontent.com/petarb33/f1-analysis/master/assets/uae_practice_3_fl_sectors.png)
![Fastest Lap in Sectors - Delta](https://raw.githubusercontent.com/petarb33/f1-analysis/master/assets/uae_practice_3_fl_sectors_delta.png)

### 8. Speed on Fastest Lap
![Speed Comparisons](https://raw.githubusercontent.com/petarb33/f1-analysis/master/assets/uae_practice_3_maxv_vs_meanv_vs_minv_comparison.png)
