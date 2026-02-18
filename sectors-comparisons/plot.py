import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import fastf1
import fastf1.plotting
import seaborn as sns
from pathlib import Path
    
    
def create_graph(data, sectors, event_info, title, label, mode='Time') -> None:
    """
    Create and save a bar plot visualizing sector performance for each driver.

    Parameters
    ----------
    data : fastf1.core.Session
        FastF1 session object containing telemetry and driver data.
    sectors : dict of pandas.DataFrame
        Dictionary containing sector time data. Keys are sector names
        ('Sector1Time', 'Sector2Time', 'Sector3Time') and values are DataFrames
        with at least 'Driver', 'Compound', and sector time columns.
    event_info : dict
        Dictionary with race or session metadata such as:
        {'round_number', 'grand_prix', 'year', 'session', 'country_code', 'country_name'}.
    title : str
        Title describing the plot (e.g., “Fastest Sector Times”).
    label : str
        Short identifier appended to the filename when saving the figure.
    mode : str, default='Time'
        Column name to use for choosing Y axis values ('Time' or 'Delta').
    """
    fig, axs = plt.subplots(ncols=1, nrows=3, figsize=(10,10))
    plt.subplots_adjust(hspace=0.3)

    drivers_colors = get_drivers_colors(data)
    tyres_colors = get_compound_colors(data)

    tyres_used = plot_sectors_time(sectors, drivers_colors, tyres_colors, axs, mode)
    style_figure_and_axes(fig, axs)
    add_fig_title(fig, event_info, title)
    add_axs_title(axs)
    add_signature(axs)
    add_legend(fig, tyres_used, tyres_colors)
    save_figure(fig, event_info, label)


def get_drivers_colors(data) -> dict[str, str]:
    """
    Get driver color mapping for plotting.

    Parameters
    ----------
    data : fastf1.core.Session
        FastF1 session object.

    Returns
    -------
    dict
        Mapping of driver abbreviations to their respective colors.
    """
    return fastf1.plotting.get_driver_color_mapping(data, colormap='default')


def get_compound_colors(data) -> dict[str, str]:
    """
    Get color mapping for tyre compounds.

    Parameters
    ----------
    data : fastf1.core.Session
        FastF1 session object.

    Returns
    -------
    dict
        Mapping of tyre compound names to their respective colors.
    """
    return fastf1.plotting.get_compound_mapping(session=data)


def plot_sectors_time(sectors, drivers_colors, tyres_colors, axs, mode='Time') -> set[str]:
    """
    Plot bar charts for each sector, grouped by driver.

    Parameters
    ----------
    sectors : dict of pandas.DataFrame
        Dictionary containing sector time data.
    drivers_colors : dict
        Mapping of driver abbreviations to their colors.
    tyres_colors : dict
        Mapping of tyre compounds to their colors.
    axs : list of matplotlib.axes.Axes
        List of Axes objects, one for each sector.
    mode : str, default='Time'
        Column name used to determine what is plotted on the Y-axis.
        - 'Time' plots absolute sector times.
        - 'Delta' plots relative differences.
        Defaults to 'Time' if not specified.

    Returns
    -------
    set
        Set of tyre compounds used in the plotted data.
    """
    tyres_used = set()
    for sector_num, sector in enumerate(['Sector1Time', 'Sector2Time', 'Sector3Time']):
        ax = axs[sector_num]
        df_to_plot = sectors[sector]

        tyres_used.update(df_to_plot['Compound'].unique())

        sns.barplot(
            x='Driver',
            y=mode,
            data=df_to_plot,
            ax=ax,
            palette=drivers_colors,
            hue='Driver'
        )

        for container in ax.containers:
            ax.bar_label(container, fontsize=7, color='white')

        apply_edgecolors(ax, df_to_plot['Compound'], tyres_colors)
        if mode == 'Time':
            set_ylim(df_to_plot, ax)
    
    return tyres_used


def set_ylim(df, ax) -> None:
    """
    Adjust Y-axis limits to add visual margin around min and max values.

    This is intended for plotting absolute sector times ['Time'] and 
    is not gonna be used when plotting deltas.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the values to be plotted.
    ax : matplotlib.axes.Axes
        Axis object for which to set the Y limits.
    mode : str
        Column name used to determine the plotted values.
    """
    min_value = df['Time'].min()
    max_value = df['Time'].max()
    margin = (max_value - min_value) * 0.2
    ax.set_ylim(min_value - margin, max_value + margin)
        

def apply_edgecolors(ax, tyre_series, color_map) -> None:
    """
    Apply edge colors to bars based on tyre compounds.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axis object containing the bar plot.
    tyre_series : pandas.Series
        Series containing tyre compound names for each bar.
    color_map : dict
        Mapping of tyre compound names to colors.
    """
    edge_colors = [color_map[tyre] for tyre in tyre_series]
    for bar, edge_color in zip(ax.patches, edge_colors):
        bar.set_edgecolor(edge_color)
        bar.set_linewidth(1.5)


def style_figure_and_axes(fig, axs) -> None:
    """
    Apply consistent styling to the figure and axes, remove axes spines,
    put on grid...

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure object.
    axs : list of matplotlib.axes.Axes
        List of axes to style.
    """
    fig.patch.set_facecolor('#292625')

    for ax in axs:
        ax.set_facecolor('#1e1c1b')
        for side in ['bottom', 'top', 'left', 'right']:
            ax.spines[side].set_visible(False)
        ax.tick_params(
            color='white',
            axis='both',
            labelcolor='white',
            labelsize=9
        )
        ax.set_xlabel('')
        ax.set_ylabel('Time (seconds)', color='white', fontsize=7.5, labelpad=7.5)
        ax.grid(
            True,
            which='major',
            axis='y',
            color='#d3d3d3',
            linestyle='--',
            linewidth=0.4,
            alpha=0.75
        )
        ax.set_axisbelow(True)


def add_fig_title(fig, event_info, title) -> None:
    """
    Add a formatted title to the figure.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure object.
    event_info : dict
        Dictionary containing event details such as round number,
        Grand Prix name, year, and session name.
    title : str
        Additional title text describing the figure.
    """
    fig.suptitle(
        f'Round {event_info['round_number']} - {event_info['grand_prix']} '
        f'{event_info['year']}\n{event_info['session']} - {title}',
        color='white',
        y=0.95
    )


def add_axs_title(axs) -> None:
    """
    Add titles for each sector subplot.

    Parameters
    ----------
    axs : list of matplotlib.axes.Axes
        List of axes to add titles to.
    """
    for i, ax in enumerate(axs, start=1):
        ax.set_title(f'Sector {i}', color='white', fontsize=10)


def add_signature(axs) -> None:
    """
    Add a signature text to the bottom-right of the last subplot.

    Parameters
    ----------
    axs : list of matplotlib.axes.Axes
        List of axes, with the signature added to the last one.
    """
    axs[2].text(
        1.06, -0.3, 'Petar B.',
        verticalalignment='bottom', horizontalalignment='right',
        transform=axs[2].transAxes,
        color='white', fontsize=10, alpha=0.7
    )


def add_legend(fig, tyres_used, tyres_colors) -> None:
    """
    Add a custom legend indicating tyre compounds.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure object.
    tyres_used : set
        Set of tyre compounds used in the plotted data.
    tyres_colors : dict
        Mapping of tyre compounds to their colors.
    """
    handles = []
    for tyre in tyres_used:
        patch = mpatches.Patch(
            facecolor='None',
            edgecolor=tyres_colors[tyre],
            linewidth=1,
            label=tyre
        )
        handles.append(patch)

    legend = fig.legend(
        handles=handles,
        title='Tyre Compound',
        loc='upper right',
        fontsize=8,
        title_fontsize=9,
        borderaxespad=1,
        frameon=False
    )
    for text in legend.get_texts():
        text.set_color('white')

    legend.get_title().set_color('white')


def save_figure(fig, event, label) -> None:
    """
    Save the provided figure to the output directory with a descriptive filename.

    The filename format is "{country_code}_{session}_{label}.png".
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
        Short identifier appended to the filename when saving the figure.
    Returns
    -------
    None
    """
    save_folder = create_output_folder(event)

    country_code = event['country_code'].lower()
    session = event['session'].lower().replace(' ', '_')

    filename = f"{country_code}_{session}_{label}.png"
    filepath = save_folder / filename

    fig.savefig(filepath, format='png', dpi=300)
    print(f"Figure saved to: {filepath}")


def create_output_folder(event) -> Path:
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
    folder_name = f"{event['year']}_r{event['round_number']:02d}_{event['country_name'].lower().replace(" ", "_")}"
    save_folder = base_folder / folder_name

    try:
        save_folder.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Could not create directory '{save_folder}': {e}")
    
    return save_folder