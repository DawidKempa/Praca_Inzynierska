import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

def fetch_state_energies(db_path="molcas_results.db", target_states=[48]):
    """Pobiera energie konkretnych stanów dla wszystkich odległości."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Pobierz wszystkie unikalne odległości
    cursor.execute("SELECT DISTINCT distance FROM calculations ORDER BY distance")
    distances = [round(row[0], 4) for row in cursor.fetchall()]
    
    # Dla każdego stanu: {distance: energy}
    energy_data = {state: {} for state in target_states}
    
    for state in target_states:
        cursor.execute("""
        SELECT distance, energy 
        FROM calculations 
        WHERE state_num = ?
        ORDER BY distance
        """, (state,))
        for d, e in cursor.fetchall():
            energy_data[state][d] = e
    
    conn.close()
    return distances, energy_data

def plot_state_energies(states_to_plot=[48], save_path="state_energies.png"):
    """Generuje wykres energii absolutnych dla wybranych stanów."""
    distances, energies = fetch_state_energies(target_states=states_to_plot)
    
    plt.figure(figsize=(12, 8))
    colors = plt.cm.plasma(np.linspace(0, 1, len(states_to_plot)))
    
    for i, state in enumerate(states_to_plot):
        x = []
        y = []
        for d in distances:
            if d in energies[state]:  # Sprawdź czy stan istnieje dla danej odległości
                x.append(d)
                y.append(energies[state][d])  # Absolutna energia
        
        plt.plot(
            x, y, 
            'o-', 
            color=colors[i],
            label=f'Stan {state}',
            markersize=6,
            linewidth=2
        )
    
    # Konfiguracja wykresu
    plt.title(f'Energia stanów w funkcji odległości', pad=20)
    plt.xlabel('Odległość międzyjądrowa (Å)', fontsize=12)
    plt.ylabel('Energia (Hartree)', fontsize=12)
    
    # Siatka
    plt.grid(True, which='both', alpha=0.3)
    plt.xticks(np.arange(0, max(distances)+0.5, 0.5))
    plt.gca().xaxis.set_minor_locator(MultipleLocator(0.1))
    
    # Legenda
    plt.legend(
        title="Numery stanów",
        bbox_to_anchor=(1.05, 1),
        loc='upper left'
    )
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    plot_state_energies(states_to_plot=[1])  # Tutaj podaj numery stanów