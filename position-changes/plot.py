import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from fastf1.core import Session
from matplotlib.axes import Axes
from matplotlib.figure import Figure


def create_graph(session_data: Session, event_info: dict) -> None:
    """Creates and saves the position change graph."""
    fig, ax = plt.subplots(figsize=(20,10)) 

    plot_positions_change(session_data, ax)
    style_figure_and_axes(fig, ax)
    add_figure_title(fig, event_info)
    add_signature(ax)
    save_figure(fig, event_info)


def plot_positions_change(session_data: Session, ax: Axes) -> None:
    """Plots the position changes for each driver in a session."""
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
    """Appies a dark theme to figure and axes, and styles ticks and labels."""
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
    """Adds a title to the figure with event information."""
    fig.suptitle(
        f'Round {event_info['round_number']} - {event_info['grand_prix']} '
        f'{event_info['year']}\n{event_info['session']} - Position Changes',
        color='white', y=0.94, fontsize=18
    )


def add_signature(ax: Axes) -> None:
    """Adds a signature to the plot."""
    ax.text(
        1.06, -0.08, 'Petar B.',
        verticalalignment='bottom',
        horizontalalignment='right',
        transform=ax.transAxes,
        color='white', fontsize=13, alpha=0.7
    )


def save_figure(fig: Figure, event: dict) -> None:
    """Saves the figure to a file in the appropriate output directory."""
    save_folder = create_output_folder(event)

    country_code = event['country_code'].lower()
    session = event['session'].lower().replace(' ', '_')

    filename = f"{country_code}_{session}_position_changes.png"
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