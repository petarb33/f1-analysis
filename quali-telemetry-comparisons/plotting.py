import itertools
from pathlib import Path
from collections.abc import Iterable
from fastf1.core import Session
from f1_types import CarDataEntry
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from typing import Union, Any
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import fastf1.utils as utils
import fastf1.plotting


# ==============================
#        MAIN GRAPH MAKERS
# ==============================

def create_full_graphs(session_data: Session, car_data: CarDataEntry,
                       event_info: dict[str, str | int]) -> None:
    """ 
    Create and save comparison graphs for all driver combinations in a session.

    For each pair of drivers in the session, this function generates a figure
    with multiple subplots showing telemetry data (speed, throttle, brake, gear),
    delta time, and cornering reference lines. Figures are styled, titled,
    and annotated with legends and signatures before being saved to disk.

    Parameters
    ----------
    session_data : fastf1.core.Session
        FastF1 session object containing telemetry and race information.
    car_data : CarDataEntry
        Dictionary containing telemetry and lap data for each driver.
    event_info : dict[str, str | int]
        Dictionary containing event metadata (e.g., 'round_number', 'grand_prix',
        'year', 'session') used for figure titles and filenames.

    Returns
    -------
    None
    """
    drivers_colors = get_drivers_colors(session_data)
    combinations = get_driver_combinations(car_data)

    for drv_a, drv_b in combinations:
        fig, axs = create_figure_with_subplots((10, 10), [1, 0.5, 0.16, 0.25])

        create_plots(axs, drv_a, drv_b, car_data, drivers_colors)
        plot_delta(axs[0], car_data[drv_a]['lap'], car_data[drv_b]['lap'], [drv_a, drv_b])
        plot_corners_vlines(session_data, axs[0])

        style_figure_and_axes(fig, axs)
        remove_borders(axs)
        add_figure_title(fig, car_data[drv_a], car_data[drv_b], event_info)
        add_legend(fig, axs[0])
        add_signature(fig)

        save_figure(fig, event_info, [drv_a, drv_b])


def create_delta_graphs(session_data: Session, car_data: CarDataEntry,
                        event_info: dict[str, str | int]) -> None:
    """
    Create and save single-axis delta comparison graphs for all driver combinations.

    For each pair of drivers in the session, this function generates a single-axis
    figure showing speed telemetry for both drivers, the delta time between them,
    and corner reference lines. The figure is styled with a dark background,
    axes labels, legends, signatures, and titles before being saved to disk.

    Parameters
    ----------
    session_data : fastf1.core.Session
        FastF1 session object containing telemetry and race information.
    car_data : CarDataEntry
        Dictionary containing telemetry and lap data for each driver.
    event_info : dict[str, str | int]
        Dictionary containing event metadata (e.g., 'round_number', 'grand_prix',
        'year', 'session') used for figure titles and filenames.

    Returns
    -------
    None
    """
    drivers_colors = get_drivers_colors(session_data)
    combinations = get_driver_combinations(car_data)

    for drv_a, drv_b in combinations:
        style = get_drivers_style(drivers_colors, drv_a, drv_b)

        fig, ax = plt.subplots(figsize=(15, 10))
        set_dark_background(fig, ax)

        for drv in (drv_a, drv_b):
            ax.plot(
                car_data[drv]['telemetry']['Distance'],
                car_data[drv]['telemetry']['Speed'],
                **style[drv],
                lw=1,
                label=drv
            )

        plot_delta(ax, car_data[drv_a]['lap'], car_data[drv_b]['lap'], [drv_a, drv_b])
        plot_corners_vlines(session_data, ax)

        ax.set_xlabel('Corner', color='white', fontsize=12, labelpad=22)
        ax.set_ylabel('Speed (km/h)', color='white', fontsize=12, labelpad=10)
        ax.set_xticks([])
        ax.tick_params(colors='white', labelsize=10, size=4, width=1)

        remove_borders(ax)
        add_figure_title(fig, car_data[drv_a], car_data[drv_b], event_info)
        add_signature(fig)
        add_legend(fig, ax)

        save_delta_figure(fig, event_info, [drv_a, drv_b])


# ==============================
#        PLOTTING HELPERS
# ==============================

def create_plots(axs: Iterable[Axes], drv_a: str, drv_b: str,
                 car_data: CarDataEntry, drivers_colors: dict[str, str]) -> None:
    """
    Create four telemetry comparison plots between two drivers.

    The function plots Speed, Throttle, Brake, and Gear data for both drivers
    on the provided Axes objects. Each telemetry line is styled according to
    the drivers' colors and predefined line weights.

    Parameters
    ----------
    axs : Iterable[matplotlib.axes.Axes]
        Collection of four Axes on which the telemetry data will be plotted.
        Each Axes corresponds to one of the following parameters:
        Speed, Throttle, Brake, and Gear.
    drv_a : str
        Driver abbreviation of the first driver.
    drv_b : str
        Driver abbreviation of the second driver.
    car_data : CarDataEntry
        Dictionary containing telemetry data for each driver.
        Must include a 'telemetry' DataFrame for both drivers, with
        'Distance', 'Speed', 'Throttle', 'Brake', and 'nGear' columns.
    drivers_colors : dict[str, str]
        Dictionary mapping drivers names to their hex color code.
    
    Returns
    -------
    None
    """
    labels = ['Speed', 'Throttle', 'Brake', 'nGear']
    line_weights = [0.8, 0.65, 0.5, 0.5]
    style = get_drivers_style(drivers_colors, drv_a, drv_b)

    for driver in (drv_a, drv_b):
        telemetry = car_data[driver]['telemetry']
        for ax, label, lw in zip(axs, labels, line_weights):
            ax.plot(
                telemetry['Distance'],
                telemetry[label],
                label=driver,
                **style[driver],
                lw=lw
            )


def plot_delta(ax: Axes, lap1, lap2, drivers: Iterable[str]) -> None:
    """
    Plot the time delta between two drivers over the lap distance.

    This function visualizes the time difference between two drivers across
    a reference lap distance. A secondary y-axis is created to display the
    delta time.

    Also removes spines.
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The primary Axes object on which the delta time curve will be drawn.
    lap1 : fastf1.core.Lap
        Lap object of the first driver, containing telemetry data.
    lap2 : fastf1.core.Lap
        Lap object of the second driver, containing telemetry data.
    drivers : Iterable[str]
        List or tuple containing the two driver identifiers in the same order
        as ``lap1`` and ``lap2``.
    
    Returns
    -------
    None
    """
    delta_time, ref_tel, _ = utils.delta_time(lap1, lap2)
    twin = ax.twinx()

    twin.plot(ref_tel['Distance'], delta_time, '--', color='white', lw=1)
    twin.tick_params(axis='y', colors='white', labelsize=9)
    twin.set_ylabel(
        f"<-- {drivers[1]} ahead | {drivers[0]} ahead -->",
        color='white', fontsize=12.5, labelpad=10
    )
    remove_borders(twin)


def plot_corners_vlines(session_data: Session, ax: Axes) -> None:
    """
    Plots vertical lines that represent corners on track on the given axis.

    Parameters
    ----------
    session_data : fastf1.core.Session
        FastF1 session object with session data.
    ax : matplotlib.axes.Axes
        Axis which will recieve the corner lines.
    
    Returns
    -------
    None
    """
    circuit_info = session_data.get_circuit_info()

    for dist in circuit_info.corners['Distance']:
        ax.axvline(x=dist, color='white', linestyle='dotted',
                   linewidth=0.5, ymin=0, ymax=1)

    bottom = ax.get_ylim()[0]
    offset = (ax.get_ylim()[1] - bottom) * 0.018
    y_pos = bottom - offset
    for _, corner in circuit_info.corners.iterrows():
        text = f"{corner['Number']}{corner['Letter']}"
        ax.text(corner['Distance'], y_pos, text, fontsize=10,
                va='center_baseline', ha='center',
                color='white')


# ==============================
#        STYLING HELPERS
# ==============================

def style_figure_and_axes(fig: Figure, axs: Iterable[Axes]) -> None:
    """
    Style the given figure and axes according to their telemetry plots.

    This function applies consistent formatting to a Matplotlib figure and
    its associated axes, setting appropriate labels, tick parameters, and
    colors that correspond to the telemetry data they represent.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure that will be colored.
    axs : Iterable[Axes]
        Collection of Axes objects whose appearance will be customized.
    
    Returns
    -------
    None
    """
    fig.patch.set_facecolor('#292625')
    labels = ['Speed (km/h)', 'Throttle (%)', 'Brake (ON/OFF)', 'nGear (-)']

    for ax, label in zip(axs, labels):
        ax.set_facecolor('#121212')
        ax.set_ylabel(label, color='white', fontsize=10, labelpad=10)
        ax.tick_params(colors='white', labelsize=10, size=4, width=1)

    axs[0].set_xticks([])
    axs[0].set_xlabel('Corner', color='white', fontsize=10, labelpad=15)

    axs[2].set_yticks([0, 1])
    axs[2].set_yticklabels(['OFF', 'ON'], color='white')

    axs[3].set_xlabel('Distance (m)', color='white', fontsize=10, labelpad=10)
    axs[3].set_yticks([2, 4, 6, 8])


def remove_borders(ax_or_axes: Union[Axes, Iterable[Axes]]) -> None:
    """
    Remove spines (borders) from one or more Matplotlib axes.

    This function hides all four spines (top, bottom, left, right) for the
    provided Axes object(s), resulting in a cleaner, borderless plot.

    Parameters
    ----------
    ax_or_axes : Union[matplotlib.axes.Axes, Iterable[matplotlib.axes.Axes]]
        Single Axes instance or an iterable of Axes instances whose spines
        will be removed.

    Returns
    -------
    None
    """
    if isinstance(ax_or_axes, plt.Axes) or not isinstance(ax_or_axes, Iterable):
        axes = [ax_or_axes]
    else:
        axes = ax_or_axes

    for ax in axes:
        for spine in ax.spines.values():
            spine.set_visible(False)


def set_dark_background(fig: Figure, ax: Axes) -> None:
    """
    Apply a dark theme to the given figure and axis.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to apply the dark theme to.
    ax : matplotlib.axes.Axes
        The axis to apply the dark theme to.

    Returns
    -------
    None
    """
    fig.patch.set_facecolor('#292625')
    ax.set_facecolor('#121212')


# ==============================
#        UTILS
# ==============================

def get_driver_combinations(car_data: CarDataEntry) -> list[tuple[str, str]]:
    """
    Returns all combinations of dictionary keys (drivers abbreviations).

    Parameters
    ----------
    car_data : CarDataEntry
        Dictionary containing telemetry data for each driver.
    
    Returns
    -------
    list
        List of tuples, where each tuple represents one driver pairing.
    """
    return list(itertools.combinations(car_data.keys(), 2))


def get_drivers_colors(session_data: Session) -> dict[str, str]:
    """
    Get a dictionary mapping driver abbreviations to their team color codes.

    The function retrieves each driver's color from the FastF1 session data
    and slightly lightens the colors of Red Bull Racing and Aston Martin
    for better visibility on dark backgrounds.

    Parameters
    ----------
    session_data : fastf1.core.Session
        FastF1 session object containing all race session data.

    Returns
    -------
    colors : dict[str, str]
        Dictionary mapping driver abbreviations to their hexadecimal color codes.
    """
    colors = fastf1.plotting.get_driver_color_mapping(session=session_data)

    for driver, color in colors.items():
        team = fastf1.plotting.get_team_name_by_driver(driver, session_data)
        if team in ('Red Bull Racing', 'Aston Martin'):
            colors[driver] = lighten_color(color)

    return colors


def get_drivers_style(drivers_colors: dict[str],
                      drv_a: str, drv_b: str) -> dict[str, dict[str, str]]:
    """
    Determines plot line styles based on driver pairings.

    The function assigns a color and line style to each driver based on
    their team color. If both drivers share the same color (e.g., teammates),
    distinct highlight colors are used to differentiate their lines.
    
    Parameters
    ----------
    drivers_colors : dict[str]
        Dictionary mapping drivers abbreviations to their hexadecimal color codes.
    drv_a : str
        Driver abbreviation of the first driver.
    drv_b : str
        Driver abbreviation of the second driver.
    
    Returns
    -------
    styles : dict[str, dict[str, str]]
        Dictionary mapping each driver to their respective line style
        configuration, including 'color' and 'linestyle' keys.
    """
    #linestyle = 'dashed' if drivers_colors[drv_a] == drivers_colors[drv_b] else 'solid'
    drv_a_color = drivers_colors[drv_a]
    drv_b_color = drivers_colors[drv_b]
    if drivers_colors[drv_a] == drivers_colors[drv_b]:
        drv_a_color = '#39FF14'
        drv_b_color = '#FF6EC7'

    return {
        drv_a: {'linestyle': 'solid', 'color': drv_a_color},
        drv_b: {'linestyle': 'solid', 'color': drv_b_color}
    }


def lighten_color(hex_color: str, factor: float = 0.2) -> str:
    """
    Lighten a hexadecimal color by a given factor.

    This function increases the brightness of a HEX color by interpolating
    each RGB component toward white. A higher factor results in a lighter color.

    Parameters
    ----------
    hex_color : str
        Hexadecimal color code (e.g., "#1E90FF") to be lightened.
    factor : float, optional
        Brightening factor in the range [0, 1]. Default is 0.2.
        A value of 0 returns the original color, while 1 returns white.

    Returns
    -------
    str
        New hexadecimal color code representing the lightened color.
    """
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)

    return f"#{r:02x}{g:02x}{b:02x}"


# ==============================
#        SAVE & TITLE HELPERS
# ==============================

def create_output_folder(event) -> Path:
    """
    Ensure the local output directory exists and return its Path.

    Builds a directory path under the repository (two levels up from this file)
    named "_output_plots/{year}_r{round_number:02d}_{country_name}/Quali". Attempts
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
    folder_name = f"{event['year']}_r{event['round_number']:02d}_{event['country_name'].lower()}/Quali"
    save_folder = base_folder / folder_name
    save_folder.mkdir(parents=True, exist_ok=True)
    return save_folder


def save_figure(fig, event, label) -> None:
    """
    Save a figure to the output directory with a descriptive filename.

    The filename is constructed as:

        "{event['country_code'].lower()}_{event['session'].lower().replace(' ', '_')}_{'vs'.join(label)}.png"

    The function ensures the output directory exists using `create_output_folder()`
    and saves the figure as a PNG at 300 DPI.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to save.
    event : dict
        Event metadata used to build the output filename. Required keys include
        'country_code' and 'session'.
    label : list[drv_a, drv_b]
        List with drivers abbreviations whose telemetries are compared.

    Returns
    -------
    None
    """
    save_folder = create_output_folder(event)
    filename = f"{event['country_code'].lower()}_{event['session'].lower().replace(' ', '_')}_{'vs'.join(label)}.png"
    fig.savefig(save_folder / filename, format='png', dpi=300)
    print(f"Figure saved to: {save_folder / filename}")


def save_delta_figure(fig, event, label) -> None:
    """
    Save a delta comparison figure to the output directory with a descriptive filename.

    This function is similar to `save_figure`, but specifically saves delta graphs
    in a subfolder named 'delta_graphs'. The output filename is constructed as:

        "{event['country_code'].lower()}_{event['session'].lower().replace(' ', '_')}_delta_{'vs'.join(label)}.png"

    The function ensures the output directory exists using `create_output_folder()` 
    and saves the figure as a PNG at 300 DPI.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to save.
    event : dict
        Event metadata used to build the output filename. Required keys include
        'country_code' and 'session'.
    label : list[drv_a, drv_b]
        List with drivers abbreviations whose telemetries are compared.

    Returns
    -------
    None
    """
    save_folder = create_output_folder(event) / "delta_graphs"
    save_folder.mkdir(parents=True, exist_ok=True)

    filename = f"{event['country_code'].lower()}_{event['session'].lower().replace(' ', '_')}_delta_{'vs'.join(label)}.png"
    fig.savefig(save_folder / filename, format='png', dpi=300)
    print(f"Delta graph saved to: {save_folder / filename}")


def add_figure_title(fig: Figure, drv_a_data: dict[str, Any],
                     drv_b_data: dict[str, Any],
                     event_info: dict[str, str | int]) -> None:
    """
    Add a formatted title to the figure containing event and driver information.

    The title summarizes the race or qualifying session, showing the round number,
    Grand Prix name, year, session type, and both drivers' lap details, positions,
    and lap times.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to which the title will be added.
    drv_a_data : dict[str, Any]
        Dictionary containing data for the first driver, including keys such as
        'lap', 'quali_phase', 'position', and 'laptime'.
    drv_b_data : dict[str, Any]
        Dictionary containing data for the second driver with the same structure
        as ``drv_a_data``.
    event_info : dict[str, str | int]
        Dictionary containing event metadata such as 'round_number',
        'grand_prix', 'year', and 'session'.

    Returns
    -------
    None
    """
    fig.suptitle(
        f"Round {event_info['round_number']} - {event_info['grand_prix']} {event_info['year']}\n"
        f"{event_info['session']} - {drv_a_data['lap'].iloc[1]} vs {drv_b_data['lap'].iloc[1]}\n"
        f"({drv_a_data['quali_phase']}) (P{drv_a_data['position']}) {drv_a_data['laptime']} vs "
        f"({drv_b_data['quali_phase']}) (P{drv_b_data['position']}) {drv_b_data['laptime']}",
        y=0.95, color='white', fontsize=13
    )


def add_legend(fig: Figure, ax: Axes) -> None:
    """
    Add a styled legend to the given figure.

    This function creates a legend for the provided figure using the labels
    from the specified Axes. The legend is styled for dark backgrounds with
    white text and a dark frame.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to which the legend will be added.
    ax : matplotlib.axes.Axes
        Axes object used to extract legend handles and labels.

    Returns
    -------
    None
    """
    handles, labels = ax.get_legend_handles_labels()
    legend = fig.legend(
        handles=handles,
        labels=labels,
        fontsize=15,
        bbox_to_anchor=(0.61, 0.67, 0.3, 0.3)
    )
    for text in legend.get_texts():
        text.set_color('white')
    legend.get_frame().set_facecolor('#121212')


def add_signature(fig: Figure) -> None:
    """
    Add a signature to the given figure.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure which will get the signature.
    
    Returns
    -------
    None
    """
    fig.text(0.95, 0.05, 'Petar B.',
             verticalalignment='bottom', horizontalalignment='right',
             color='white', fontsize=10, alpha=0.7)


# ==============================
#        FIGURE HELPERS
# ==============================

def create_figure_with_subplots(figsize: Iterable, height_ratios: Iterable) -> tuple[Figure, list[Axes]] :
    """
    Create a Matplotlib figure with vertically stacked subplots using GridSpec.

    This function generates a figure of the specified size and creates subplots
    arranged in a single column with customizable height ratios. It also adjusts
    the vertical spacing between subplots.

    Parameters
    ----------
    figsize : Iterable
        Figure size as (width, height) in inches.
    height_ratios : Iterable
        List or tuple of relative heights for each subplot. The length of this
        iterable determines the number of subplots.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The created Matplotlib figure.
    axs : list[matplotlib.axes.Axes]
        List of subplot Axes objects in top-to-bottom order.
    """
    fig = plt.figure(figsize=figsize)
    fig.subplots_adjust(hspace=0.4)
    gs = gridspec.GridSpec(len(height_ratios), 1, height_ratios=height_ratios)
    axs = [fig.add_subplot(gs[i]) for i in range(len(height_ratios))]

    return fig, axs
