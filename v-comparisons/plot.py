from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

import fastf1
import fastf1.plotting


def plot_speed_comparisons(
    session_data, min_speeds, mean_speeds, max_speeds, event
):
    """
    Generate and save bar charts for comparing driver speeds on their fastest lap.

    Function orchestrates the creation of five figures:
    - Max speed per driver
    - Min speed per driver
    - Mean speed per driver
    - Max vs Min speed comparison
    - Max vs Mean vs Min speed comparison

    Parameters
    ----------
    session_data : fastf1.core.Session
        Loaded FastF1 session object.
    min_speeds : pandas.DataFrame
        DataFrame with columns ['Driver', 'Speed'] representing min speeds.
    mean_speeds : pandas.DataFrame
        DataFrame with columns ['Driver', 'Speed'] representing mean speeds.
    max_speeds : pandas.DataFrame
        DataFrame with columns ['Driver', 'Speed'] representing max speeds.
    event : dict
        Dictionary containing metadata about the race session, used for
        labeling plots and organizing output.
    """
    colors = get_driver_colors(session_data)
    
    plot_max_graph(max_speeds, colors, event)
    plot_min_graph(min_speeds, colors, event)
    plot_mean_graph(mean_speeds, colors, event)
    plot_min_max_graph(min_speeds, max_speeds, colors, event)
    plot_min_mean_max_graph(min_speeds, mean_speeds, max_speeds, colors, event)


def get_driver_colors(session):
    """
    Retrieve a dictionary mapping each driver to their default FastF1 color.

    Parameters
    ----------
    session : fastf1.core.Session
        Loaded FastF1 session object.

    Returns
    -------
    dict
        Mapping of driver abbreviations to hex color codes.
    """

    return fastf1.plotting.get_driver_color_mapping(session, colormap='default')


def plot_max_graph(max_speeds, colors, event):
    """
    Create and save a bar chart showing maxiumum speed per driver on their fastest lap.

    Parameters
    ----------
    max_speeds : pandas.DataFrame
        DataFrame with columns ['Driver', 'Speed'] representing max speeds.
    colors : dict
        Dictionary mapping driver abbreviations to hex color codes.
    event : dict
        Metadata dictionary with event information used for titles and saving.
    
    Returns
    -------
    None
    """
    fig, ax = plt.subplots(figsize=(10, 10))

    barplot(ax, max_speeds, colors, 'Max Speed on the Fastest Lap')

    style_figure(fig, ax, event, 'Max V on the Fastest Lap')
    save_figure(fig, event, 'maxv')


def plot_min_graph(min_speeds, colors, event):
    """
    Create and save a bar chart showing minimum speed per driver on their fastest lap.

    Parameters
    ----------
    min_speeds : pandas.DataFrame
        DataFrame with columns ['Driver', 'Speed'] representing minimum speeds.
    colors : dict
        Dictionary mapping driver abbreviations to hex color codes.
    event : dict
        Metadata dictionary with event information used for titles and saving.
    
    Returns
    -------
    None
    """
    fig, ax = plt.subplots(figsize=(10, 10))

    barplot(ax, min_speeds, colors, 'Min Speed on the Fastest Lap')

    style_figure(fig, ax, event, 'Min V on the Fastest Lap')
    save_figure(fig, event, 'minv')


def plot_mean_graph(mean_speeds, colors, event):
    """
    Create and save a bar chart showing mean speed per driver on their fastest lap.

    Parameters
    ----------
    min_speeds : pandas.DataFrame
        DataFrame with columns ['Driver', 'Speed'] representing mean speeds.
    colors : dict
        Dictionary mapping driver abbreviations to hex color codes.
    event : dict
        Metadata dictionary with event information used for titles and saving.
    
    Returns
    -------
    None
    """
    fig, ax = plt.subplots(figsize=(10, 10))

    barplot(ax, mean_speeds, colors, 'Mean Speed on the Fastest Lap')

    style_figure(fig, ax, event, 'Mean V on the Fastest Lap')
    save_figure(fig, event, 'meanv')


def plot_min_max_graph(min_speeds, max_speeds, colors, event):
    """
    Create and save a bar chart showing both maximum and minimum speed
    per driver on their fastest lap, on the same figure.

    Parameters
    ----------
    min_speeds : pandas.DataFrame
        DataFrame with columns ['Driver', 'Speed'] representing minimum speeds.
    max_speeds : pandas.DataFrame
        DataFrame with columns ['Driver', 'Speed'] representing maximum speeds.
    colors : dict
        Dictionary mapping driver abbreviations to hex color codes.
    event : dict
        Metadata dictionary with event information used for titles and saving.
    
    Returns
    -------
    None
    """
    fig, axs = plt.subplots(nrows=2, figsize=(10, 10))
    
    barplot(axs[0], max_speeds, colors, 'Max Speed on the Fastest Lap')
    barplot(axs[1], min_speeds, colors, 'Min Speed on the Fastest Lap')
    
    style_figure(fig, axs, event, "Max/Min V Comparison on Fastest Lap")
    save_figure(fig, event, "maxv_vs_minv")


def plot_min_mean_max_graph(min_speeds, mean_speeds, max_speeds, colors, event):
    """
    Create and save a bar chart showing maximum, mean and minimum speed
    per driver on their fastest lap, on the same figure.

    Parameters
    ----------
    min_speeds : pandas.DataFrame
        DataFrame with columns ['Driver', 'Speed'] representing minimum speeds.
    mean_speeds : pandas.DataFrame
        DataFrame with columns ['Driver', 'Speed'] representing mean speeds.
    max_speeds : pandas.DataFrame
        DataFrame with columns ['Driver', 'Speed'] representing maximum speeds.
    colors : dict
        Dictionary mapping driver abbreviations to hex color codes.
    event : dict
        Metadata dictionary with event information used for titles and saving.
    
    Returns
    -------
    None
    """
    fig, axs = plt.subplots(nrows=3, figsize=(10, 10))
    fig.subplots_adjust(hspace=0.3)
    
    barplot(axs[0], max_speeds, colors, 'Max Speed on the Fastest Lap')
    barplot(axs[1], mean_speeds, colors, 'Mean Speed on the Fastest Lap')
    barplot(axs[2], min_speeds, colors, 'Min Speed on the Fastest Lap')

    style_figure(
        fig, axs, event,
        "Max/Mean/Min V Comparison on Fastest Lap"
    )
    save_figure(fig, event, "maxv_vs_meanv_vs_minv")


def barplot(ax, df, colors, title=None):
    """
    Render a seaborn barplot of driver speeds on the given axis.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axis for plotting.
    df : pandas.DataFrame
        DataFrame with that will be plotted, with columns ['Driver', 'Speed']
    colors : dict
        Dictionary mapping drivers abbreviations to their hex color codes.

    Returns
    -------
    None
    """
    sns.barplot(
        data=df, x='Driver', y='Speed',
        hue='Driver', palette=colors, ax=ax
    )

    for container in ax.containers:
        ax.bar_label(container, fontsize=9, color='white')

    min_speed = df['Speed'].min()
    max_speed = df['Speed'].max()
    ax.set_ylim(int(min_speed) - 1, int(max_speed) + 1)

    if title is not None:
        ax.set_title(title, color='white', fontsize=10)

def style_figure(fig, axs, event, title):
    """
    Apply dark-themed styling to a figure and it's axes, label all the axes,
    remove axis borders, add signature to the last axis and display the given title.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to style.
    axs : Union[matplotlib.axis.Axes, list]
        One or more axes to style.
    event : dict
        Metadata for labeling the figure.
    title : str
        Title to display

    Returns
    -------
    None
    """
    fig.patch.set_facecolor('#292625')

    if not isinstance(axs, list):
        axs = [axs]

    axs = np.ravel(axs)

    for ax in axs:
        ax.set_facecolor('#1e1c1b')
        ax.tick_params(
            colors='white', labelcolor='white', labelsize=9
        )
        ax.set_xlabel('')
        ax.set_ylabel(
            'Speed (km/h)', color='white',
            fontsize=7.5, labelpad=7.5
        )
        for side in ['bottom', 'top', 'left', 'right']:
            ax.spines[side].set_visible(False)

    axs[-1].text(
        1.06, len(axs) * -0.1, 'Petar B.',
        ha='right', va='bottom',
        transform=axs[-1].transAxes,
        color='white', fontsize=10, alpha=0.7
    )

    fig.suptitle(
        f"Round {event['round_number']} - {event['grand_prix']} {event['year']}\n"
        f"{event['session']} - {title}",
        color='white', y=0.95
    )

def save_figure(fig, event, label):
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
    label : str
        Label describing the type of the plot.

    Returns
    -------
    None
    """
    save_folder = create_output_folder(event)

    country_code = event['country_code'].lower()
    session = event['session'].lower().replace(' ', '_')
    safe_label = label.lower().replace(' ', '_')

    filename = f"{country_code}_{session}_{safe_label}_comparison.png"
    filepath = save_folder / filename

    fig.savefig(filepath, format='png', dpi=300)
    print(f"Figure saved to: {filepath}")

def create_output_folder(event):
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
    folder_name = f"{event['year']}_r{event['round_number']:02d}_{event['country_name'].lower().replace(' ', '_')}"
    save_folder = base_folder / folder_name

    try:
        save_folder.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Could not create directory '{save_folder}': {e}")
    
    return save_folder
