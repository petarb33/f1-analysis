from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

import fastf1
import fastf1.plotting


def plot_speed_comparisons(
    session_data, min_speeds, mean_speeds, max_speeds, event
):
    colors = get_driver_colors(session_data)
    
    plot_max_graph(max_speeds, colors, event)
    plot_min_graph(min_speeds, colors, event)
    plot_mean_graph(mean_speeds, colors, event)
    plot_min_max_graph(min_speeds, max_speeds, colors, event)
    plot_min_mean_max_graph(min_speeds, mean_speeds, max_speeds, colors, event)


def get_driver_colors(session):
    return fastf1.plotting.get_driver_color_mapping(session, colormap='default')


def plot_max_graph(max_speeds, colors, event):
    fig, ax = plt.subplots(figsize=(10, 10))

    barplot(ax, max_speeds, colors, 'Max Speed on the Fastest Lap')

    style_figure(fig, ax, event, 'Max V on the Fastest Lap')
    save_figure(fig, event, 'maxv')


def plot_min_graph(min_speeds, colors, event):
    fig, ax = plt.subplots(figsize=(10, 10))

    barplot(ax, min_speeds, colors, 'Min Speed on the Fastest Lap')

    style_figure(fig, ax, event, 'Min V on the Fastest Lap')
    save_figure(fig, event, 'minv')


def plot_mean_graph(mean_speeds, colors, event):
    fig, ax = plt.subplots(figsize=(10, 10))

    barplot(ax, mean_speeds, colors, 'Mean Speed on the Fastest Lap')

    style_figure(fig, ax, event, 'Mean V on the Fastest Lap')
    save_figure(fig, event, 'meanv')


def plot_min_max_graph(min_speeds, max_speeds, colors, event):
    fig, axs = plt.subplots(nrows=2, figsize=(10, 10))
    
    barplot(axs[0], max_speeds, colors, 'Max Speed on the Fastest Lap')
    barplot(axs[1], min_speeds, colors, 'Min Speed on the Fastest Lap')
    
    style_figure(fig, axs, event, "Max/Min V Comparison on Fastest Lap")
    save_figure(fig, event, "maxv_vs_minv")


def plot_min_mean_max_graph(min_speeds, mean_speeds, max_speeds, colors, event):
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
    save_folder = create_output_folder(event)

    country_code = event['country_code'].lower()
    session = event['session'].lower().replace(' ', '_')
    safe_label = label.lower().replace(' ', '_')

    filename = f"{country_code}_{session}_{safe_label}_comparison.png"
    filepath = save_folder / filename

    fig.savefig(filepath, format='png', dpi=300)
    print(f"Figure saved to: {filepath}")

def create_output_folder(event):
    base_folder = Path(__file__).parent.parent / "_output_plots"
    folder_name = f"{event['year']}_r{event['round_number']:02d}_{event['country_name'].lower().replace(' ', '_')}"
    save_folder = base_folder / folder_name

    try:
        save_folder.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Could not create directory '{save_folder}': {e}")
    
    return save_folder
