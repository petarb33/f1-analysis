import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
from typing import Dict
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from pathlib import Path

SESSION_COLORS = {"Q1": "#b2df8a", "Q2": "#66c2a5", "Q3": "#1b7837"}

def create_graph(quali_data, event_info, fig_width) -> None:
    """
    Create and save a qualifying gap-to-pole figure.

    This is the top-level helper that instantiates the Matplotlib figure and axes,
    composes the plot by calling the plotting and styling helpers, and saves the
    final figure.

    Parameters
    ----------
    quali_data : pandas.DataFrame
        DataFrame containing qualifying rows with at least the columns
        'Driver', 'LapTime', 'Session' and 'GapToPole'
    event_info : dict
        Dictionary with event metadata used for the figure title and output
        filename.
    fig_width : float
        Width of the created figure in inches. The height is fixed at 10 inches.

    Returns
    -------
    None
    """
    fig, ax = plt.subplots(figsize=(fig_width, 10))

    plot_data(ax, quali_data)
    style_figure_and_axes(fig, ax)
    add_figure_title(fig, event_info)
    add_signature(ax)
    add_legend(ax)
    save_figure(fig, event_info, fig_width)

def plot_data(ax: Axes, quali_data: pd.DataFrame) -> None:
    """
    Plot horizontal bars representing each driver's gap to pole on given Axes.

    The function iterates over rows in `quali_data`, draws a horizontal bar per
    driver colored by qualifying session (Q1/Q2/Q3), labels the bar with the
    lap time for pole or a +gap string otherwise, and tracks the
    maximum bar width to set an appropriate x-axis limit.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes object where the horizontal bars will be drawn.
    quali_data : pandas.DataFrame
        DataFrame with qualifying results; each row should expose attributes
        'Driver', 'LapTime', 'Session', and 'GapToPole' when accessed via
        itertuples().

    Returns
    -------
    None
    """
    max_width = 0
    for row in quali_data.itertuples():
        session = getattr(row, "Session", None)
        driver = getattr(row, "Driver", None)
        delta = getattr(row, "GapToPole", None)

        if driver is None or delta is None or session is None:
            continue

        color = SESSION_COLORS.get(session, "#888888")

        bar = ax.barh(driver, delta, left=0, color=color)            
        rect = bar[0]
        width = rect.get_width()
        max_width = max(width, max_width)

        if delta == 0:
            ax.bar_label(bar, labels=[convert_time(getattr(row, "LapTime"))], padding=3, color='white')
        else:
            ax.bar_label(bar, labels=[f'+{delta}'], padding=3,  color='white')
        
    ax.invert_yaxis()
    ax.set_xlim(0, max_width * 1.1)


def style_figure_and_axes(fig: Figure, ax: Axes) -> None:
    """
    Apply a dark theme and style axes labels, ticks, and spines.

    This function configures the figure and axes facecolors for a dark theme,
    sets the x-axis label with readable styling, adjusts tick parameters to be
    visible on a dark background, and hides the axis spines for a cleaner look.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Matplotlib Figure containing the Axes.
    ax : matplotlib.axes.Axes
        Axes to style.

    Returns
    -------
    None
    """
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
    """
    Add a suptitle to the figure describing the event and session.

    The title follows the format "Round {round_number} - {grand_prix}{year}
    Qualifying - Gap To Pole". The function reads values from `event_info`
    using .get() to tolerate missing keys.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The Figure to which the title will be applied.
    event_info : dict
        Event metadata; expected keys include 'round_number', 'grand_prix',
        and 'year'.

    Returns
    -------
    None
    """
    round_number = event_info.get("round_number", "")
    grand_prix = event_info.get("grand_prix", "")
    year = event_info.get("year", "")
    session = event_info.get("session", "")

    fig.suptitle(
        f'Round {round_number} - {grand_prix}'
        f' {year}\n{session} - Gap To Pole',
        color='white',
        y=0.937,
        fontsize=15
    )
    
def add_signature(ax: Axes) -> None:
    """
    Draw a small signature text on the plot.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes on which to draw the signature.

    Returns
    -------
    None
    """
    ax.text(
        1.01,
        -0.08,
        'Petar B.',
        verticalalignment='bottom',
        horizontalalignment='right',
        transform=ax.transAxes,
        color='white',
        fontsize=10,
        alpha=0.7
    )
    
def add_legend(ax: Axes) -> None:
    """
    Add a legend explaining the color mapping for qualifying sessions.

    Constructs legend patches for Q1, Q2 and Q3 using the SESSION_COLORS
    mapping and attaches the legend to the axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes that will receive the legend.

    Returns
    -------
    None
    """
    legend_patches = [
        mpatches.Patch(color=SESSION_COLORS["Q1"], label="Q1 Lap"),
        mpatches.Patch(color=SESSION_COLORS["Q2"], label="Q2 Lap"),
        mpatches.Patch(color=SESSION_COLORS["Q3"], label="Q3 Lap"),
    ]

    ax.legend(
        handles=legend_patches,
        loc='upper right',
        labelcolor='white',
        facecolor='#292625'
    )


def save_figure(fig: Figure, event: dict, size: int) -> None:
    """
    Save the provided figure to the output directory with a descriptive filename.

    The filename format is "{country_code}_{session}_gap_to_pole_{size}x10.png".
    This function creates the required output directory via create_output_folder()
    and writes the PNG at 300 DPI.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to save.
    event : dict
        Event metadata used to build the output filename. Required keys include
        'country_code' and 'session'.
    size : int
        Width used in the filename (corresponds to the fig_width supplied to
        create_graph), the height is fixed to 10 inches in the filename and
        the actual saved figure.

    Returns
    -------
    None
    """
    save_folder = create_output_folder(event)

    country_code = event['country_code'].lower()
    session = event['session'].lower().replace(' ', '_')

    filename = f"{country_code}_{session}_gap_to_pole_{size}x10.png"
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

def convert_time(laptime: float) -> str:
    """
    Convert a lap time in seconds to a formatted "M:SS.sss" string.

    Parameters
    ----------
    laptime : float
        Lap time in seconds.

    Returns
    -------
    str
        Formatted lap time as "M:SS.sss" (minutes and seconds with 3 decimals).
    """
    minute = int(laptime // 60)
    seconds = laptime - minute * 60
    return f"{minute}:{seconds:06.3f}"