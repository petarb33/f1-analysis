import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
from typing import Dict
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from pathlib import Path

def create_graph(quali_data, event_info, fig_width):
    """Creates and saves the graph."""
    fig, ax = plt.subplots(figsize=(fig_width, 10))

    plot_data(ax, quali_data)
    style_figure_and_axes(fig, ax)
    add_figure_title(fig, event_info)
    add_signature(ax)
    add_legend(ax)
    save_figure(fig, event_info, fig_width)

def plot_data(ax: Axes, quali_data: pd.DataFrame) -> None:
    """Plots the gap to pole position for each driver in a session"""
    max_width = 0
    for row in quali_data.itertuples():
        session = row.Session
        driver = row.Driver
        delta = row.GapToPole

        if session == 'Q1':
            color = '#b2df8a'
        elif session == 'Q2':
            color = '#66c2a5'
        elif session == 'Q3':
            color = '#1b7837'

        bar = ax.barh(driver, delta, left=0, color=color)
            
        rect = bar[0]
        width = rect.get_width()
        max_width = max(width, max_width)

        if delta == 0:
            ax.bar_label(bar, labels=[convert_time(row.LapTime)], padding=3, color='white')
        else:
            ax.bar_label(bar, labels=[f'+{row.GapToPole}'], padding=3,  color='white')
        
    ax.invert_yaxis()
    plt.xlim(0, max_width * 1.1)


def style_figure_and_axes(fig: Figure, ax: Axes) -> None:
    """Appies a dark theme to figure and axes, and styles ticks and labels."""
    fig.patch.set_facecolor('#292625')
    ax.set_facecolor('#1e1c1b')

    ax.set_xlabel('Gap To Pole (s)', color='white', labelpad=10, fontsize=15)
    
    ax.tick_params(
        color='white',
        axis='both',
        labelcolor='white',
        labelsize=12
    )

    for side in ['bottom', 'top', 'left', 'right']:
        ax.spines[side].set_visible(False)


def add_figure_title(fig: Figure, event_info: Dict) -> None:
    """Adds a title to the figure with event information."""
    fig.suptitle(
        f'Round {event_info['round_number']} - {event_info['grand_prix']}'
        f'{event_info['year']}\nQualifying - Gap To Pole',
        color='white', y=0.937, fontsize=15
    )
    
def add_signature(ax: Axes) -> None:
    """Adds a signature to the plot"""
    ax.text(
        1.01, -0.08, 'Petar B.',
        verticalalignment='bottom',
        horizontalalignment='right',
        transform=ax.transAxes,
        color='white', fontsize=10, alpha=0.7
    )
    
def add_legend(ax: Axes) -> None:
    """Adds a legend describing in what session is each lap done"""
    legend_patches = [
        mpatches.Patch(color='#b2df8a', label='Q1 Lap'),
        mpatches.Patch(color='#66c2a5', label='Q2 Lap'),
        mpatches.Patch(color='#1b7837', label='Q3 Lap')
    ]

    ax.legend(
        handles=legend_patches,
        loc='upper right',
        labelcolor='white',
        facecolor='#292625'
    )


def save_figure(fig: Figure, event: dict, size: int) -> None:
    """Saves the figure to a file in the appropriate output directory."""
    save_folder = create_output_folder(event)

    country_code = event['country_code'].lower()
    session = event['session'].lower().replace(' ', '_')

    filename = f"{country_code}_{session}_gap_to_pole_{size}x10.png"
    filepath = save_folder / filename

    fig.savefig(filepath, format='png', dpi=300)
    print(f"Figure saved to: {filepath}")


def create_output_folder(event: dict) -> Path:
    """Creates the directory structure for saving output plots."""
    base_folder = Path(__file__).parent.parent / "_output_plots"
    folder_name = f"{event['year']}_r{event['round_number']:02d}_{event['country_name'].lower()}"
    save_folder = base_folder / folder_name

    try:
        save_folder.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Could not create directory '{save_folder}': {e}")
    
    return save_folder

def convert_time(laptime: float) -> str:
    minute = int(laptime // 60)
    seconds = laptime - minute * 60
    return f"{minute}:{seconds:06.3f}"