import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import fastf1
import fastf1.plotting
import seaborn as sns
from pathlib import Path
    
    
def create_graph(data, sectors, event_info, plot_func, title, label):
    fig, axs = plt.subplots(ncols=1, nrows=3, figsize=(10,10))
    plt.subplots_adjust(hspace=0.3)

    drivers_colors = get_drivers_colors(data)
    tyres_colors = get_compound_colors(data)
    tyres_used = get_tyres_used(sectors[1]['Tyre'], tyres_colors)

    plot_func(sectors, drivers_colors, tyres_colors, axs)
    style_figure_and_axes(fig, axs)
    add_fig_title(fig, event_info, title)
    add_axs_title(axs)
    add_signature(axs)
    add_legend(fig, tyres_used)
    save_figure(fig, event_info, label)


def get_tyres_used(tyres_series, tyres_colors):
    tyres_used = {}
    for tyre in tyres_series:
        if tyre not in tyres_used.keys():
            tyres_used[tyre] = tyres_colors[tyre]

    return tyres_used


def get_drivers_colors(data):
    return fastf1.plotting.get_driver_color_mapping(data, colormap='default')


def get_compound_colors(data):
    return fastf1.plotting.get_compound_mapping(session=data)


def plot_sectors_time(sectors, drivers_colors, tyres_colors, axs):
    for sector_num in range(3):
        ax = axs[sector_num]
        df = sectors[sector_num + 1]

        sns.barplot(
            x='Driver',
            y='Time',
            data=df,
            ax=ax,
            palette=drivers_colors,
            hue='Driver'
        )

        for container in ax.containers:
            ax.bar_label(container, fontsize=7, color='white')

        apply_edgecolors(ax, df['Tyre'], tyres_colors)

        min_value = df['Time'].min()
        max_value = df['Time'].max()
        ax.set_ylim(int(min_value) - 1, max_value + 0.3)


def plot_sectors_delta(sectors, drivers_colors, tyres_colors, axs):
    for sector_num in range(3):
        ax = axs[sector_num]
        df = sectors[sector_num + 1]

        sns.barplot(
            x='Driver',
            y='Delta',
            data=df,
            ax=ax,
            palette=drivers_colors,
            hue='Driver'
        )
    
        for i, container in enumerate(ax.containers):
            labels = [f"{df['Time'].iloc[0]}"] if i == 0 else None
            color = 'fuchsia' if i == 0 else 'white'
            ax.bar_label(container, labels=labels, fontsize=7, color=color)

        apply_edgecolors(ax, df['Tyre'], tyres_colors)


def apply_edgecolors(ax, tyre_series, color_map):
    edge_colors = [color_map[tyre] for tyre in tyre_series]
    for bar, edge_color in zip(ax.patches, edge_colors):
        bar.set_edgecolor(edge_color)
        bar.set_linewidth(1)


def style_figure_and_axes(fig, axs):
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


def add_fig_title(fig, event_info, title):
    fig.suptitle(
        f'Round {event_info['round_number']} - {event_info['grand_prix']} '
        f'{event_info['year']}\n{event_info['session']} - {title}',
        color='white',
        y=0.95
    )


def add_axs_title(axs):
    for i, ax in enumerate(axs, start=1):
        ax.set_title(f'Sector {i}', color='white', fontsize=10)


def add_signature(axs):
    axs[2].text(
        1.06, -0.3, 'Petar B.',
        verticalalignment='bottom', horizontalalignment='right',
        transform=axs[2].transAxes,
        color='white', fontsize=10, alpha=0.7
    )


def add_legend(fig, tyres_used):
    handles = []
    for tyre, color in tyres_used.items():
        patch = mpatches.Patch(
            facecolor='None',
            edgecolor=color,
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


def save_figure(fig, event, label):
    save_folder = create_output_folder(event)

    country_code = event['country_code'].lower()
    session = event['session'].lower().replace(' ', '_')

    filename = f"{country_code}_{session}_{label}.png"
    filepath = save_folder / filename

    fig.savefig(filepath, format='png', dpi=300)
    print(f"Figure saved to: {filepath}")


def create_output_folder(event):
    base_folder = Path(__file__).parent.parent / "_output_plots"
    folder_name = f"{event['year']}_r{event['round_number']:02d}_{event['country_name'].lower()}"
    save_folder = base_folder / folder_name

    try:
        save_folder.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Could not create directory '{save_folder}': {e}")
    
    return save_folder