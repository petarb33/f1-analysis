import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import fastf1
import fastf1.plotting
import fastf1.utils as utils
from pathlib import Path
from collections.abc import Iterable
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from fastf1.core import Laps

def create_graph(car_data, session_data, event_info) -> None:
    """
    Create a multi-panel telemetry comparison graph for two drivers.

    Parameters
    ----------
    car_data : dict
        A dictionary containing processed lap information for each driver.
        Expected structure for each driver:
        {
            'lap_number': int,
            'laptime': Timedelta,
            'lap_object': fastf1.core.Laps,
            'telemetry': pandas.DataFrame
        }
    session_data : fastf1.core.Session
        Full session data used to compute driver colors and corner markers.
    event_info : dict
        Metadata describing the event. Expected keys:
        ``'round_number'``, ``'grand_prix'``, ``'year'``, ``'session'``.

    Returns
    -------
    None
    """
    fig, axs = prepare_axes()
    
    drivers, lap_numbers, lap_times, lap_objects = extract_lap_metadata(car_data)

    drivers_colors = get_drivers_colors(session_data)
    
    create_plots(axs, car_data, drivers_colors)
    plot_delta(axs[0], lap_objects, drivers)
    plot_corners_vlines(session_data, axs[0])

    style_figure_and_axes(fig, axs)
    add_figure_title(fig, event_info, lap_numbers, lap_times, drivers)
    add_signature(fig)
    remove_borders(axs)
    add_legend(fig, axs[0])

    save_figure(fig, event_info, drivers, lap_numbers)

def prepare_axes(figsize=(10, 10), height_ratios=None) -> tuple[Figure, Axes]:
    """
    Create a figure and vertically stacked axes for telemetry plotting.

    Parameters
    ----------
    figsize : tuple, optional
        Figure size passed to `plt.figure`.
    height_ratios : list of float, optional
        Ratios defining the relative height of each subplot. If None,
        defaults to ``[1, 0.6, 0.3, 0.3]``.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The created figure.
    axs : list of matplotlib.axes.Axes
        A list of subplot axes arranged vertically.
    """
    if height_ratios is None:
        height_ratios = [1, 0.6, 0.3, 0.3]

    fig = plt.figure(figsize=figsize)
    fig.subplots_adjust(hspace=0.4)

    gs = gridspec.GridSpec(len(height_ratios), 1, height_ratios=height_ratios)
    axs = [fig.add_subplot(gs[i]) for i in range(len(height_ratios))]

    return fig, axs

def extract_lap_metadata(car_data) -> tuple[list[str], list[str], list[str], list[Laps]]:
    """
    Extract drivers, lap numbers, lap times, and lap objects from `car_data`.

    Parameters
    ----------
    car_data : dict
        Dictionary mapping driver abbreviations to lap information.

    Returns
    -------
    drivers : list of str
        Driver identifiers in the order stored in the dict.
    lap_numbers : list of str
        Formatted lap numbers (strings) for each driver.
    lap_times : list of str
        Formatted lap times (strings) for each driver.
    lap_objects : list of pandas.DataFrame
        The actual lap objects used for delta plotting.
    """
    drivers = list(car_data.keys())

    lap_numbers = [str(data['lap_number']) for data in car_data.values()]
    lap_times   = [str(data['laptime']) for data in car_data.values()]
    lap_objects = [data['lap_object'] for data in car_data.values()]
    
    return drivers, lap_numbers, lap_times, lap_objects


def create_plots(axs, car_data, drivers_colors) -> None:
    """
    Plot telemetry comparisons for multiple drivers across several axes.

    Parameters
    ----------
    axs : list of matplotlib.axes.Axes
        A list of axes objects on which the telemetry data will be plotted.
        Expected order of axes corresponds to:
        ``['Speed', 'Throttle', 'Brake', 'nGear']``.
    car_data : dict
        Dictionary containing telemetry data for each driver.
        Expected structure:
        ``car_data[driver] = {'telemetry': DataFrame, ...}``,
        where the telemetry DataFrame includes the columns
        ``'Distance'``, ``'Speed'``, ``'Throttle'``, ``'Brake'``, and ``'nGear'``.
    drivers_colors : dict
        Mapping defining hex code color to drivers abbreviations for each driver,
        passed to `get_drivers_style()` to generate plotting styles.

    Returns
    -------
    None
    """
    labels = ['Speed', 'Throttle', 'Brake', 'nGear']
    line_weights = [0.8, 0.65, 0.5, 0.5]
    drivers = list(car_data.keys())
    style = get_drivers_style(drivers_colors, drivers[0], drivers[1])

    for driver in car_data.keys():
        telemetry = car_data[driver]['telemetry']
        for ax, label, lw in zip(axs, labels, line_weights):
            ax.plot(
                telemetry['Distance'],
                telemetry[label],
                label=driver,
                **style[driver],
                lw=lw
            )

def plot_delta(ax, laps, drivers) -> None:
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
    laps : list of fastf1.core.Lap
        List of Lap objects of the first driver and second driver, containing telemetry data.
    drivers : Iterable[str]
        List or tuple containing the two driver identifiers in the same order
        as ``laps[0]`` and ``laps[1]``.
    
    Returns
    -------
    None
    """
    lap1 = laps[0]
    lap2 = laps[1]
    delta_time, ref_tel, _ = utils.delta_time(lap1, lap2)
    twin = ax.twinx()

    twin.plot(ref_tel['Distance'], delta_time, '--', color='white', lw=1)
    twin.tick_params(axis='y', colors='white', labelsize=9)
    twin.set_ylabel(
        f"<-- {drivers[1]} ahead | {drivers[0]} ahead -->",
        color='white', fontsize=12.5, labelpad=10
    )
    remove_borders(twin)

def plot_corners_vlines(session_data, ax) -> None:
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

def style_figure_and_axes(fig, axs) -> None:
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

    xmin, xmax = axs[3].get_xlim()
    y_ticks = axs[3].get_yticks()
    axs[3].hlines(y_ticks, xmin=xmin, xmax=xmax, colors='white', linestyles='--', alpha=0.4, linewidth=0.5)



def add_figure_title(fig, event_info, lap_numbers, lap_times, drivers) -> None:
    """
    Add a formatted title to the figure summarizing event and lap comparison details.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure object to which the title will be added.
    event_info : dict
        Dictionary containing metadata about the event. Expected keys:
        - ``'round_number'`` : int  
            The round number of the race.
        - ``'grand_prix'`` : str  
            The Grand Prix name (e.g., "Monaco", "Japan").
        - ``'year'`` : int  
            Event year.
        - ``'session'`` : str  
            Session type (e.g., "Race", "Qualifying", "FP2").
    lap_numbers : tuple or list of int
        Two lap numbers being compared, corresponding to the drivers in `drivers`.
    drivers : tuple or list of str
        Driver identifiers (e.g., ``["VER", "HAM"]``) in the same order
        as `lap_numbers`.

    Returns
    -------
    None
    """
    fig.suptitle(
        f"Round {event_info['round_number']} - {event_info['grand_prix']} {event_info['year']}\n"
        f"{event_info['session']} - {drivers[0]} vs {drivers[1]}\n"
        f"Lap {lap_numbers[0]} vs Lap {lap_numbers[1]}\n"
        f"{lap_times[0]} vs {lap_times[1]}",
        y=0.965, color='white', fontsize=13
    )

def add_signature(fig) -> None:
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

def remove_borders(ax_or_axes) -> None:
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

def add_legend(fig, ax) -> None:
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

def get_drivers_colors(session_data) -> dict[str, str]:
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

def create_output_folder(event) -> Path:
    """
    Ensure the local output directory exists and return its Path.

    Builds a directory path under the repository (two levels up from this file)
    named "_output_plots/{year}_r{round_number:02d}_{country_name}/Telemetry". Attempts
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
    folder_name = f"{event['year']}_r{event['round_number']:02d}_{event['country_name'].lower()}/Telemetry"
    save_folder = base_folder / folder_name
    save_folder.mkdir(parents=True, exist_ok=True)
    return save_folder


def save_figure(fig, event, drivers, lap_numbers) -> None:
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
    drivers : list[driver1, driver2]
        List with drivers abbreviations whose telemetries are compared.
    lap_numbers: list[lap_number1, lap_number2]
        List with lap numbers of laps that are compared.
    Returns
    -------
    None
    """
    save_folder = create_output_folder(event)
    filename = f"{event['country_code'].lower()}_{event['session'].lower().replace(' ', '_')}_{'vs'.join(drivers)}_lap{'-'.join(lap_numbers)}.png"
    fig.savefig(save_folder / filename, format='png', dpi=300)
    print(f"Figure saved to: {save_folder / filename}")