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
    """
    Create and save a race stints graph comparing multiple drivers.

    This function handles plotting driver stints, styling the figure,
    adding title, legend, signature, and saving the output image.

    Parameters
    ----------
    drivers : list of str
        List of driver abbreviations to compare.
    stints : dict of str -> dict of int -> pd.DataFrame
        Dictionary mapping driver to their stints (stint_number -> laps DataFrame).
    event_info : dict
        Metadata for the event. Expected keys: 'round_number', 'grand_prix', 'year', 'country_code', 'country_name'.
    session_data : fastf1.core.Session
        FastF1 session object containing race data.

    Returns
    -------
    None
    """
    fig, ax = plt.subplots(figsize=(15,10))

    used_tyres = get_used_tyres(stints)
    driver_styles = get_drivers_styles(drivers, session_data)
    compound_colors = get_compound_colors(session_data, used_tyres)

    plot_stints(drivers, ax, stints, driver_styles, compound_colors)
    style_figure_and_ax(fig, ax, session_data.total_laps)
    add_figure_title(fig, event_info, drivers)
    add_signature(ax)
    add_legend(ax, compound_colors, driver_styles)
    save_figure(fig, drivers, event_info)


def get_drivers_styles(
    drivers: list[str],
    session_data: Session
) -> dict[str, dict[str, str]]:
    """
    Generate a dictionary of driver line styles and colors.

    If two drivers have the same color, the second gets a dotted linestyle
    to distinguish them visually.

    Parameters
    ----------
    drivers : list of str
        List of driver abbreviations.
    session_data : fastf1.core.Session
        FastF1 session object for color reference.

    Returns
    -------
    dict of str -> dict
        Maps driver abbreviation to a dictionary with keys 'color' and 'linestyle'.
    """
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


def get_used_tyres(stints: dict[str, dict[int, pd.DataFrame]]) -> list[str]:
    """
    Extract all tyre compounds used by drivers during the race.

    Parameters
    ----------
    stints : dict of str -> dict of int -> pd.DataFrame
        Dictionary mapping driver to their stints (stint_number -> laps DataFrame).

    Returns
    -------
    list of str
        List of all tyre compounds used by any driver.
    """
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
    """
    Map tyre compounds to their respective colors.

    Parameters
    ----------
    session_data : fastf1.core.Session
        FastF1 session object with session data.
    used_tyres : list of str
        List of tyre compounds used in the race.

    Returns
    -------
    compound_colors : dict of str -> str
        Mapping of used compound name to hex color.
    """
    compound_colors = {tyre:None for tyre in used_tyres}
    for tyre in used_tyres:
        compound_colors[tyre] = fastf1.plotting.get_compound_color(tyre, session_data)

    return compound_colors


def plot_stints(
    drivers: list[str],
    ax: Axes,
    stints: dict[str, pd.DataFrame],
    driver_colors: dict[str, str],
    compound_colors: dict[str, str]
) -> None:
    """
    Plot stints with driver colors and tyre markers.
    
    Parameters
    ----------
    drivers : list of str
        List of drivers (drivers abbreviations) whose laps are compared.
    ax : matplotlib.axes.Axes
        Axes on which the comparison will be drawn.
    stints : dict[str, dict[int, pd.DataFrame]]
        Dictionary of driver to {stint_number -> laps DataFrame}.
    drivers_colors : dict
        Dictionary mapping driver to drivers hex code colors.
    compound_colors : dict
        Dictionary mapping compound names to their hex code colors.

    Returns
    -------
    None 
    """
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
    """
    Apply visual styling to the figure and axes for better readability.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to style.
    ax : matplotlib.axes.Axes
        Axes to style.
    total_laps : int
        Total number of laps in the race.

    Returns
    -------
    None
    """
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
    """
    Add title to the figure.
    
    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure which will recieve the title.
    event_info : dict
        Metadata dict with information needed for the title.
    drivers : list of str
        Drivers whose laps are compared, that will be printed in the title.

    Returns
    -------
    None
    """
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
    """
    Add legends for tyres and drivers.
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes which will recieve the legend.
    used_tyres : dict
        Dictionary mapping tyres names to their hex code colors.
    drivers_styles : dict
        Dictionary mapping drivers abbreviations to their colors and line styles.
    
    Returns
    -------
    None
    """
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
    """
    Adds signature to the bottom right corner of the given axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes that will get the signature.
    
    Returns
    -------
    None
    """
    ax.text(
        1.01, -0.08, 'Petar B.',
        verticalalignment='bottom',
        horizontalalignment='right',
        transform=ax.transAxes,
        color='white', fontsize=10, alpha=0.7
    )


def save_figure(fig: Figure, drivers: list[str], event: dict) -> None:
    """
    Save the provided figure to the output directory with a descriptive filename.

    The filename format is "{country_code}_{'vs'.join(drivers)}.png".
    This function creates the required output directory via create_output_folder()
    and writes the PNG at 300 DPI.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to save.
    event : dict
        Event metadata used to build the output filename. Required keys include
        'country_code' and 'session'.
    drivers : list of str
        List of drivers whose laps are compared.

    Returns
    -------
    None
    """
    save_folder = create_output_folder(event)

    country_code = event['country_code'].lower()

    filename = f"{country_code}_{'vs'.join(drivers)}.png"
    filepath = save_folder / filename

    fig.savefig(filepath, format='png', dpi=300)
    print(f"Figure saved to: {filepath}")


def create_output_folder(event: dict) -> Path:
    """
    Ensure the local output directory exists and return its Path.

    Builds a directory path under the repository (two levels up from this file)
    named "_output_plots/{year}_r{round_number:02d}_{country_name}". Attempts
    to create the directory if it does not already exist. If creation fails
    the exception is printed and the attempted Path object is still returned.

    Parameters
    ----------
    event : dict
        Event metadata; expected keys include 'year', 'round_number', and
        'country_name'.

    Returns
    -------
    pathlib.Path
        Path to the output folder (created if possible).
    """
    base_folder = Path(__file__).parent.parent / "_output_plots"
    folder_name = f"{event['year']}_r{event['round_number']:02d}_{event['country_name'].lower()}"
    save_folder = base_folder / folder_name

    try:
        save_folder.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Could not create directory '{save_folder}': {e}")
    
    return save_folder