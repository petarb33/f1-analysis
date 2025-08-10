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
    """Creates and saves comparison graphs for all driver combinations."""
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
    """Creates and saves single-axis delta graphs for all driver combinations."""
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
    """Generates telemetry plots for selected drivers."""
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
    """Plots time delta between 2 drivers."""
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
    """Plots vertical lines and labels for each corner."""
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
    """Applies a dark theme to figure and axes."""
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
    """Removes plot borders for given axis/axes."""
    if isinstance(ax_or_axes, plt.Axes) or not isinstance(ax_or_axes, Iterable):
        axes = [ax_or_axes]
    else:
        axes = ax_or_axes

    for ax in axes:
        for spine in ax.spines.values():
            spine.set_visible(False)


def set_dark_background(fig: Figure, ax: Axes) -> None:
    """Applies a dark theme to both figure and axis."""
    fig.patch.set_facecolor('#292625')
    ax.set_facecolor('#121212')


# ==============================
#        UTILS
# ==============================

def get_driver_combinations(car_data: CarDataEntry) -> list[tuple[str, str]]:
    """Returns all possible driver pair combinations."""
    return list(itertools.combinations(car_data.keys(), 2))


def get_drivers_colors(session_data: Session) -> dict[str, str]:
    """Retrieves and lightens (some) F1 driver team colors."""
    colors = fastf1.plotting.get_driver_color_mapping(session=session_data)

    for driver, color in colors.items():
        team = fastf1.plotting.get_team_name_by_driver(driver, session_data)
        if team in ('Red Bull Racing', 'Aston Martin'):
            colors[driver] = lighten_color(color)

    return colors


def get_drivers_style(drivers_colors: dict[str],
                      drv_a: str, drv_b: str) -> dict[str, dict[str, str]]:
    """Determines plot line styles based on driver pairings."""
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
    """Lightens a HEX color by a given factor."""
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
    """Creates the directory structure for saving output plots."""
    base_folder = Path(__file__).parent.parent / "_output_plots"
    folder_name = f"{event['year']}_r{event['round_number']:02d}_{event['country_name'].lower()}/Quali"
    save_folder = base_folder / folder_name
    save_folder.mkdir(parents=True, exist_ok=True)
    return save_folder


def save_figure(fig, event, label) -> None:
    """Saves the figure to the output folder."""
    save_folder = create_output_folder(event)
    filename = f"{event['country_code'].lower()}_{event['session'].lower().replace(' ', '_')}_{'vs'.join(label)}.png"
    fig.savefig(save_folder / filename, format='png', dpi=300)
    print(f"Figure saved to: {save_folder / filename}")


def save_delta_figure(fig, event, label) -> None:
    """Saves delta figures to a subfolder."""
    save_folder = create_output_folder(event) / "delta_graphs"
    save_folder.mkdir(parents=True, exist_ok=True)

    filename = f"{event['country_code'].lower()}_{event['session'].lower().replace(' ', '_')}_delta_{'vs'.join(label)}.png"
    fig.savefig(save_folder / filename, format='png', dpi=300)
    print(f"Delta graph saved to: {save_folder / filename}")


def add_figure_title(fig: Figure, drv_a_data: dict[str, Any],
                     drv_b_data: dict[str, Any],
                     event_info: dict[str, str | int]) -> None:
    """Adds a title to the figure with event information."""
    fig.suptitle(
        f"Round {event_info['round_number']} - {event_info['grand_prix']} {event_info['year']}\n"
        f"{event_info['session']} - {drv_a_data['lap'].iloc[1]} vs {drv_b_data['lap'].iloc[1]}\n"
        f"({drv_a_data['quali_phase']}) (P{drv_a_data['position']}) {drv_a_data['laptime']} vs "
        f"({drv_b_data['quali_phase']}) (P{drv_b_data['position']}) {drv_b_data['laptime']}",
        y=0.95, color='white', fontsize=13
    )


def add_legend(fig: Figure, ax: Axes) -> None:
    """Adds a styled legend to the figure."""
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
    """Adds a signature to the plot."""
    fig.text(0.95, 0.05, 'Petar B.',
             verticalalignment='bottom', horizontalalignment='right',
             color='white', fontsize=10, alpha=0.7)


# ==============================
#        FIGURE HELPERS
# ==============================

def create_figure_with_subplots(figsize: Iterable, height_ratios: Iterable) -> tuple[Figure, list[Axes]] :
    """Creates a figure with subplots arranged in GridSpec."""
    fig = plt.figure(figsize=figsize)
    fig.subplots_adjust(hspace=0.4)
    gs = gridspec.GridSpec(len(height_ratios), 1, height_ratios=height_ratios)
    axs = [fig.add_subplot(gs[i]) for i in range(len(height_ratios))]

    return fig, axs
