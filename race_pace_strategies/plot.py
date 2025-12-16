import matplotlib.pyplot as plt
import fastf1.plotting
import os
import pandas as pd
from fastf1.core import Session
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from pathlib import Path

def get_drivers_colors(session_data: Session) -> dict[str, str]:
    return fastf1.plotting.get_driver_color_mapping(session_data, colormap='default')
    

def create_multi_graph(
    race_data: Session,
    laps: pd.DataFrame,
    stints: pd.DataFrame,
    drivers_order: pd.DataFrame,
    drivers_colors: dict[str, str],
    drivers: list[str],
    event_info: dict[str, str | int]
) -> None:
    """
    Create a combined visualization of race pace and driver strategies.

    This function generates a two-panel figure:
      - The top subplot shows a boxplot of drivers' lap times (race pace),
        sorted by mean lap time.
      - The bottom subplot shows each driver's stints as horizontal bars,
        colored by tyre compound to represent race strategy.

    Parameters
    ----------
    race_data : fastf1.core.Session
        FastF1 session object containing race information.
    laps : pd.DataFrame
        Laps dataframe with all drivers laps.
    stints : pd.DataFrame
        DataFrame with stints that will be plotted
    drivers_order : pd.DataFrame
        DataFrame that represents order of drivers mean lap times.
    drivers_colors : dict[str, str]
        Drivers colors for the boxplot.
    drivers : list[str]
        List of driver identifiers (e.g., 'VER', 'HAM', 'NOR') whose
        stints will be plotted.
    event_info : dict[str, str | int]
        Metadata dictionary with event information.

    Returns
    -------
    None
    """
    fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(10, 10), gridspec_kw={'height_ratios': [1.3, 1]})

    plot_laps(laps, drivers_order, axs[0], drivers_colors)
    plot_stints(race_data, stints, drivers, axs[1])
    style_fig_and_axs(fig, axs)
    add_figure_title(fig, event_info)
    add_ax_title(axs[0], 'Race Pace - Sorted by Mean Laptime')
    add_ax_title(axs[1], 'Race Strategies - Sorted by Race Results')
    add_ylabel(axs[0])
    add_signature(axs[1])
    save_figure(fig, event_info, 'race_pace_strategies')


def create_pace_graph(
    laps: pd.DataFrame,
    drivers_order: pd.DataFrame,
    drivers_colors: dict[str, str],
    event_info: dict[str, str | int]
) -> None:
    """
    Create and style a graph that represents drivers race pace.

    Parameters
    ----------
    laps : pd.DataFrame
        Laps dataframe with all drivers laps.
    drivers_order : pd.DataFrame
        DataFrame that represents order of drivers mean lap times.
    drivers_colors : dict[str, str]
        Drivers colors for the boxplot.
    event_info : dict[str, str | int]
        Metadata dictionary with event information.

    Returns
    -------
    None
    """
    fig, ax = plt.subplots(figsize=(15, 10))

    plot_laps(laps, drivers_order, ax, drivers_colors)
    style_fig_and_axs(fig, ax)
    add_figure_title(fig, event_info)
    add_ax_title(ax, 'Race Pace - Sorted by Mean Laptime')
    add_ylabel(ax)
    add_signature(ax)
    save_figure(fig, event_info, 'race_pace')


def create_stints_graph(
    race_data: Session,
    stints: pd.DataFrame,
    drivers: list[str],
    event_info: dict[str, str | int]
) -> None:
    """
    Create and style a graph that represent drivers strategies.

    Parameters
    ----------
    race_data : fastf1.core.Session
        FastF1 session object containing race data and metadata.
    stints : pd.DataFrame
        DataFrame with stints that will be plotted.
    drivers : list[str]
        List of driver identifiers (e.g., 'VER', 'HAM', 'NOR') whose
        stints will be plotted.
    event_info : dict[str, str | int]
        Metadata dictionary with event information.

    Returns
    -------
    None
    """
    fig, ax = plt.subplots(figsize=(10, 10))

    plot_stints(race_data, stints, drivers, ax)
    style_fig_and_axs(fig, ax)
    add_figure_title(fig, event_info)
    add_ax_title(ax, 'Race Strategies - Sorted by Race Results')
    add_signature(ax)
    save_figure(fig, event_info, 'strategies')

def plot_laps(
    laps: pd.DataFrame,
    drivers_order: pd.DataFrame,
    ax: Axes,
    drivers_colors: dict[str, str | int]
) -> None:
    """
    Plot laps with boxplot to represent drivers pace.

    Parameters
    ----------
    laps : pd.DataFrame
        Laps dataframe with all drivers laps.
    drivers_order : pd.DataFrame
        DataFrame that represents order of drivers mean lap times.
    ax : matplotlib.axes.Axes
        Matplotlib Axes object where boxplot will be drawn.
    drivers_colors : dict[str, str]
        Drivers colors for the boxplot.
    
    Returns
    -------
    None
    """
    data = [laps.loc[laps['Driver'] == driver, 'LapTime (s)'].values
            for driver in drivers_order]
    drv_colors = [drivers_colors[drv] for drv in drivers_order]

    boxplot = ax.boxplot(
        x=data,
        labels=drivers_order,
        patch_artist=True,
        meanline=True,
        showmeans=True,
        meanprops={'color': 'black', 'linestyle': '--', 'linewidth': 1},
        medianprops={'color': 'black', 'linestyle': '-', 'linewidth': 1},
        boxprops={'color': 'white', 'linewidth': 1},
        whiskerprops={'color': 'white', 'linewidth': 1},
        capprops={'color': 'white'},
        showfliers=False
    )

    for patch, color in zip(boxplot['boxes'], drv_colors):
        patch.set_facecolor(color)
    
def plot_stints(
    race_data: Session,
    stints: pd.DataFrame,
    drivers: list[str],
    ax: Axes
) -> None:
    """
    Plot driver stints to visualize race strategies.

    Each horizontal bar represents a stint for a driver, where the
    width corresponds to the number of laps in that stint and the
    color indicates the tyre compound used.

    Parameters
    ----------
    race_data : fastf1.core.Session
        FastF1 session object containing race data and metadata.
    stints : pd.DataFrame
        DataFrame with stints that will be plotted.
    drivers : list[str]
        List of driver identifiers (e.g., 'VER', 'HAM', 'NOR') whose
        stints will be plotted.
    ax : matplotlib.axes.Axes
        Matplotlib Axes object where the stints will be drawn.
    
    Returns
    -------
    None
    """
    for driver in drivers:
        driver_stints = stints.loc[stints['Driver'] == driver]

        prev_stint_end = 0
        for idx, row in driver_stints.iterrows():
            compound_color = fastf1.plotting.get_compound_color(
                row['Compound'], session=race_data
            )

            ax.barh(
                y=driver,
                width=row['StintLength'],
                left=prev_stint_end,
                color=compound_color,
                edgecolor='black',
                fill=True
            )

            prev_stint_end += row['StintLength']
    
    ax.invert_yaxis()


def style_fig_and_axs(fig: Figure, axs: Axes | list[Axes]) -> None:
    """
    Apply a consistent dark style to a Matplotlib figure and its axes.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure object to be styled.
    axs : matplotlib.axes.Axes or list[matplotlib.axes.Axes]
        Single Axes instance or list of Axes to apply the style to.

    Returns
    -------
    None
    """
    fig.patch.set_facecolor('#292625')

    if isinstance(axs, Axes):
        axs = [axs]

    spines = ['left', 'right', 'top', 'bottom']

    for ax in axs:
        ax.set_facecolor('#1e1c1b')
        ax.tick_params(colors='white') 
        for side in spines:
            ax.spines[side].set_visible(False)
        

def add_ylabel(ax: Axes) -> None:
    """
    Sets axes Y label to 'LapTime (s)'

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes which will get the Y label change.
    
    Returns
    -------
    None
    """
    ax.set_ylabel('LapTime (s)', color='white', fontsize=10)


def add_figure_title(fig: Figure, event_info: dict[str, str | int]) -> None:
    """
    Add figure title to given figure.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure which will recieve the title.
    event_info : dict
        Metadata with event information, needed for the title.

    Returns
    -------
    None
    """
    fig.suptitle(
        f'Round {event_info['round_number']} - '
        f'{event_info['grand_prix']} {event_info['year']}\n',
        color='white', 
        y=0.93
    )


def add_ax_title(ax: Axes, title: str) -> None:
    """
    Add title to given axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes which will recieve the title.
    title : str
        Title that will be put.

    Returns
    -------
    None
    """
    ax.set_title(title, color='white')


def add_signature(ax: Axes) -> None:
    """
    Adds signature on given axes.

    Parameters
    ----------
    ax : Axes
        Axes on which will signature be written on
    
    Returns
    -------
    None
    """
    ax.text(
        1.06, -0.1, 'Petar B.',
        verticalalignment='bottom', horizontalalignment='right',
        transform=ax.transAxes,
        color='white', fontsize=10, alpha=0.7
    )


def save_figure(fig: Figure, event: dict, suffix: str) -> None:
    """
    Save the provided figure to the output directory with a descriptive filename.

    The filename format is "{country_code}_{suffix}.png".
    This function creates the required output directory via create_output_folder()
    and writes the PNG at 300 DPI.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to save.
    event : dict
        Event metadata used to build the output filename. Required keys include
        'country_code' and 'session'.
    label : str
        Label describing the type of the plot.

    Returns
    -------
    None
    """
    save_folder = create_output_folder(event)

    country_code = event['country_code'].lower()

    filename = f"{country_code}_{suffix}.png"
    filepath = save_folder / filename

    fig.savefig(filepath, format='png', dpi=400)
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
    save_folder = base_folder / folder_name.replace(" ", "_")

    try:
        save_folder.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Could not create directory '{save_folder}': {e}")
    
    return save_folder