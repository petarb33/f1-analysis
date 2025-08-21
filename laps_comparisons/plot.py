import matplotlib.pyplot as plt
import fastf1
import fastf1.plotting
import numpy as np
import matplotlib.lines as mlines
import pandas as pd
from fastf1.core import Session
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from pathlib import Path

def create_graph(
    drivers: list[str],
    stints: dict[str, pd.DataFrame],
    event_info: dict[str, str | int],
    session_data: Session
) -> None:
    """Main function to create and save a race stints graph."""
    fig, ax = plt.subplots(figsize=(15,10))

    used_tyres = get_used_tyres(stints)
    driver_styles = get_drivers_styles(drivers, session_data)
    compound_colors, tyres_dict = get_compound_colors(session_data, used_tyres)

    plot_stints(drivers, ax, stints, driver_styles, compound_colors)
    style_figure_and_ax(fig, ax, session_data.total_laps)
    add_figure_title(fig, event_info, drivers)
    add_signature(ax)
    add_legend(ax, tyres_dict, driver_styles)
    save_figure(fig, drivers, event_info)


def get_drivers_styles(
    drivers: list[str],
    session_data: Session
) -> dict[str, dict[str, str]]:
    """Return driver styles with unique line styles for duplicate colors."""
    driver_styles, seen_colors = {}, set()

    for drv in drivers:
        color = fastf1.plotting.get_driver_color(drv, session=session_data)

        linestyle = 'solid'
        if color in seen_colors:
            linestyle = 'dotted'
        else:
            seen_colors.add(color)

        driver_styles[drv] = {'color': color, 'linestyle': linestyle}
    
    return driver_styles


def get_used_tyres(stints: dict[str, pd.DataFrame]) -> list[str]:
    """Return a list of all tyre compounds used in stints."""
    used_tyres = set()
    for drv_stints in stints.values():
        for stint in drv_stints.values():
            compound = stint['Compound'].iloc[0]
            used_tyres.add(compound)

    return list(used_tyres)


def get_compound_colors(
    session_data: Session,
    used_tyres: list[str]
) -> tuple[dict[str, str], dict[str, str]]:
    """Return compound color mappings for used tyres."""
    compound_colors = {tyre:None for tyre in used_tyres}
    for tyre in used_tyres:
        compound_colors[tyre] = fastf1.plotting.get_compound_color(tyre, session_data)

    return fastf1.plotting.get_compound_mapping(session_data), compound_colors


def plot_stints(
    drivers: list[str],
    ax: Axes,
    stints: dict[str, pd.DataFrame],
    driver_colors: dict[str, str],
    compound_colors: dict[str, str]
) -> None:
    """Plot stints with driver colors and tyre markers."""
    for drv in drivers:
        for stint_number in stints[drv].keys():
            stint = stints[drv][stint_number]

            ax.plot(
                stint['LapNumber'],
                stint['LapTime (s)'],
                **driver_colors[drv]
            )

            ax.scatter(
                stint['LapNumber'],
                stint['LapTime (s)'],
                c=compound_colors[stint['Compound'].iloc[0]],
                edgecolor=driver_colors[drv]['color'], s=80, zorder=3
            )


def style_figure_and_ax(fig: Figure, ax: Axes, total_laps: int) -> None:
    """Apply styling to figure and axes."""
    fig.patch.set_facecolor('#292625')
    ax.set_facecolor('#1e1c1b')

    spines = ['right', 'left', 'bottom', 'top']
    for spine in spines:
        ax.spines[spine].set_visible(False)

    ticks = np.arange(1, total_laps+1)
    
    ax.tick_params(
        which='both',
        color='white',
        axis='both',
        labelcolor='white',
        labelsize=9,
        size=5
    )

    ax.set_xticks(ticks)
    fontsize = 8
    if len(ticks) > 55:
        fontsize = 7
    ax.set_xticklabels(ticks, fontsize=fontsize)

    ax.set_xlabel('Lap', color='white', fontsize=10, labelpad=10)
    ax.set_ylabel('LapTime (s)', color='white', fontsize=10, labelpad=10)
    
    ax.grid(True, axis="x", linestyle="-", linewidth=0.6, alpha=0.2)
    ax.grid(True, axis="y", linestyle='--', linewidth=0.6, alpha=0.5)


def add_figure_title(fig: Figure, event_info: dict, drivers: list[str]) -> None:
    """Add title to the figure."""
    fig.suptitle(
        f'Round {event_info['round_number']} - {event_info['grand_prix']} '
        f'{event_info['year']}\n{' vs '.join(drivers)}',
        color='white', y=0.937, fontsize=15
    )


def add_legend(
    ax: Axes,
    used_tyres: dict[str, str],
    drivers_styles: dict[str, dict[str, str]]
) -> None:
    """Add legends for tyres and drivers."""
    tyres_handles = [
        mlines.Line2D([], [], color=tyre_color, marker='o',
                      linestyle=None, markersize=10, label=tyre_name)
        for tyre_name, tyre_color in used_tyres.items()
    ]

    drivers_handles = [
        mlines.Line2D([], [], color=drv_style['color'],
                      linestyle=drv_style['linestyle'], linewidth=2, label=drv_name)
        for drv_name, drv_style in drivers_styles.items()
    ]

    tyre_legend = ax.legend(
        handles=tyres_handles, loc='upper right',  bbox_to_anchor=(0.92, 1), 
        facecolor='#292625', labelcolor='white', title='Tyres')
    tyre_legend.get_title().set_color('white') 

    driver_legend = ax.legend(
        handles=drivers_handles, loc='upper right',
        facecolor='#292625', labelcolor='white', title='Drivers')
    driver_legend.get_title().set_color('white') 
    
    ax.add_artist(tyre_legend)
    ax.add_artist(driver_legend)


def add_signature(ax: Axes) -> None:
    """Add signature to the graph."""
    ax.text(
        1.01, -0.08, 'Petar B.',
        verticalalignment='bottom',
        horizontalalignment='right',
        transform=ax.transAxes,
        color='white', fontsize=10, alpha=0.7
    )


def save_figure(fig: Figure, drivers: list[str], event: dict) -> None:
    """Saves the figure to a file in the appropriate output directory."""
    save_folder = create_output_folder(event)

    country_code = event['country_code'].lower()

    filename = f"{country_code}_{'vs'.join(drivers)}.png"
    filepath = save_folder / filename

    fig.savefig(filepath, format='png', dpi=400)
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