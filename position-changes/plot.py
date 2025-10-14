import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from fastf1.core import Session
from matplotlib.axes import Axes
from matplotlib.figure import Figure


def create_graph(session_data: Session, event_info: dict) -> None:
    """
    Create and save a line plot showing driver position changes over the race.

    This function initializes the figure, plots each driver's position trace,
    applies styling, adds metadata and signature, and saves the final output.

    Parameters
    ----------
    session_data : fastf1.core.Session
        Loaded session object containing lap-by-lap race data.
    event_info : dict
        Metadata dictionary containing event details such as round number,
        grand prix name, year, session type, and country information.

    Returns
    -------
    None
    """
    fig, ax = plt.subplots(figsize=(20,10)) 

    plot_positions_change(session_data, ax)
    style_figure_and_axes(fig, ax)
    add_figure_title(fig, event_info)
    add_signature(ax)
    save_figure(fig, event_info)


def plot_positions_change(session_data: Session, ax: Axes) -> None:
    """
    Plot each driver's position change across laps in the given session.

    Uses FastF1 styling to render a line for each driver showing their
    position evolution throughout the race. Adds a styled legend to the axis.
    
    Parameters
    ----------
    session_data : fastf1.core.Session
        Loaded session object containing lap data for all drivers
    ax : matplotlib.axes.Axes
        Axis object on which to draw the position changes.
    
    Returns
    -------
    None
    """
    for driver in session_data.drivers:
        driver_laps = session_data.laps.pick_drivers(driver)
        abb = driver_laps['Driver'].iloc[0]

        style = fastf1.plotting.get_driver_style(
            identifier=abb,
            style=['color', 'linestyle'],
            session=session_data
        )
        
        sns.lineplot(
            data=driver_laps,
            x='LapNumber',
            y='Position',
            label=abb,
            **style
        )
    
    ax.legend(
        bbox_to_anchor=(1.0, 1.01),
        labelcolor='white',
        facecolor='#1e1c1b',
        edgecolor='white',
        fontsize=18
    )


def style_figure_and_axes(fig: Figure, ax: Axes) -> None:
    """
    Applies dark theme to figure and axis, sets labels, styles ticks
    and removes spines.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to style.
    ax : matplotlib.axes.Axes
        Axis to style.
    
    Returns
    -------
    None
    """
    fig.patch.set_facecolor('#292625')
    ax.set_facecolor('#1e1c1b')

    ax.set_xlabel('Lap', color='white', labelpad=5, fontsize=15)
    ax.set_ylabel('Position', color='white', labelpad=5, fontsize=15)
    ax.set_yticks([1, 5, 10, 15, 20])

    ax.tick_params(
        color='white',
        axis='both',
        labelcolor='white',
        labelsize=12
    )

    ax.invert_yaxis()

    for side in ['bottom', 'top', 'left', 'right']:
        ax.spines[side].set_visible(False)


def add_figure_title(fig: Figure, event_info: dict) -> None:
    """
    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure on which title will be displayed.
    event_info : dict
        Metadata dictionary with keys like 'round_number', 'grand_prix' and
        'year' needed for the title.
    
    Returns
    -------
    None
    """
    fig.suptitle(
        f'Round {event_info['round_number']} - {event_info['grand_prix']} '
        f'{event_info['year']}\n{event_info['session']} - Position Changes',
        color='white', y=0.94, fontsize=18
    )


def add_signature(ax: Axes) -> None:
    """
    Adds little signature on the bottom right corner.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axis on which signature will be displayed.

    Returns
    -------
    None
    """
    ax.text(
        1.06, -0.08, 'Petar B.',
        verticalalignment='bottom',
        horizontalalignment='right',
        transform=ax.transAxes,
        color='white', fontsize=13, alpha=0.7
    )


def save_figure(fig: Figure, event: dict) -> None:
    """
    Save the provided figure to the output directory with a descriptive filename.

    The filename format is "{country_code}_{session}_position_changes.png".
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
    session = event['session'].lower().replace(' ', '_')

    filename = f"{country_code}_{session}_position_changes.png"
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