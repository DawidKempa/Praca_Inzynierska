import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator
from matplotlib.lines import Line2D

def fetch_state_data(db_path="molcas_results.db", target_states=[48]):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT distance FROM calculations ORDER BY distance")
    distances = [round(row[0], 4) for row in cursor.fetchall()]

    energy_data = {}
    multiplicities = {}

    for state in target_states:
        cursor.execute("""
        SELECT distance, energy, multiplicity 
        FROM calculations 
        WHERE state_num = ?
        ORDER BY distance
        """, (state,))
        energy_data[state] = {}
        multiplicities[state] = None
        for d, e, m in cursor.fetchall():
            energy_data[state][d] = e
            if m is not None:
                multiplicities[state] = m

    conn.close()
    return distances, energy_data, multiplicities

def get_color_by_multiplicity(multiplicity):
    if multiplicity == 1:
        return 'blue'
    elif multiplicity == 3:
        return 'green'
    elif multiplicity == 5:
        return 'red'
    else:
        return 'gray'

def plot_state_energies(states_to_plot=[48], save_path="state_energies.png"):
    distances, energies, multiplicities = fetch_state_data(target_states=states_to_plot)
    
    fig, ax = plt.subplots(figsize=(14, 10))

    all_energies = []
    for state_data in energies.values():
        all_energies.extend(state_data.values())

    if not all_energies:
        print("Brak danych energetycznych do wykresu.")
        return

    E_min = min(all_energies)
    y_min = -150
    y_max = -146
    print(f"Skala osi Y: od {y_min:.3f} do {y_max:.3f} Hartree (E_min = {E_min:.6f})")

    for i, state in enumerate(states_to_plot):
        x = []
        y = []
        for d in distances:
            if d in energies[state]:
                x.append(d)
                y.append(energies[state][d])

        if not x or not y:
            continue

        multiplicity = multiplicities.get(state)
        color = get_color_by_multiplicity(multiplicity)
        label = f"Stan {state} (M={multiplicity})"

        ax.plot(
            x, y,
            'o-',
            color=color,
            label=label,
            markersize=3,
            linewidth=1.2,
            alpha=0.8
        )

        x_pos = x[-1]
        y_pos = y[-1]
        offset_y = 0.15 * ((i % 6) - 3)

        ax.annotate(
            f"{state} (M={multiplicity})",
            xy=(x_pos, y_pos),
            xytext=(x_pos + 0.5, y_pos + offset_y),
            textcoords='data',
            arrowprops=dict(arrowstyle='->', lw=0.7, color=color, alpha=0.6),
            fontsize=8,
            color=color,
            alpha=0.9
        )

    ax.set_ylim(y_min, y_max)
    ax.set_title('Energie stanów w funkcji odległości', pad=20)
    ax.set_xlabel('Odległość międzyjądrowa (Å)', fontsize=12)
    ax.set_ylabel('Energia (Hartree)', fontsize=12)
    ax.grid(True, which='both', alpha=0.3)
    ax.set_xticks(np.arange(0, max(distances) + 0.5, 0.5))
    ax.xaxis.set_minor_locator(MultipleLocator(0.1))

    legend1 = ax.legend(
        title="Numery i multipletowość stanów",
        loc='upper center',
        bbox_to_anchor=(0.5, -0.1),  # legenda wyżej
        ncol=6,
        fontsize='small',
        title_fontsize='medium',
        frameon=False
    )
    ax.add_artist(legend1)

    color_legend_elements = [
        Line2D([0], [0], color='blue', lw=2, label='Singlet (M=1)'),
        Line2D([0], [0], color='green', lw=2, label='Triplet (M=3)'),
        Line2D([0], [0], color='red', lw=2, label='Kwintet (M=5)'),
        Line2D([0], [0], color='gray', lw=2, label='Inne / brak danych')
    ]
    ax.legend(
        handles=color_legend_elements,
        title="Kolory wg multipletowości",
        loc='center left',
        bbox_to_anchor=(1.02, 0.5),
        fontsize='small',
        title_fontsize='medium',
        frameon=False
    )

    plt.subplots_adjust(bottom=0.2, right=0.82)

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    plot_state_energies(states_to_plot=list(range(1, 99)))
