# symmetry_plotter.py
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

# Konfiguracja
DB_PATH = "molcas_results.db"

# Kolory dla różnych wartości Λ (abs_m)
LAMBDA_COLORS = {
    0: '#1f77b4',  # Σ - niebieski
    1: '#ff7f0e',  # Π - pomarańczowy
    2: '#2ca02c',  # Δ - zielony
    3: '#d62728',  # Φ - czerwony
    4: '#9467bd'   # Γ - fioletowy
}

# Kolory dla multipletowości (jasne odcienie)
MULTIPLICITY_COLORS = {
    1: '#a6cee3',  # singlet - jasny niebieski
    3: '#fdbf6f',  # triplet - jasny pomarańczowy
    5: '#b2df8a'   # kwintet - jasny zielony
}

# Style linii dla różnych multipletowości
MULTIPLICITY_STYLES = {
    1: '-',  # singlet - linia ciągła
    3: ':',  # triplet - linia kropkowana
    5: '--'  # kwintet - linia kreskowana
}

# Nazwy multipletowości
MULTIPLICITY_NAMES = {
    1: 'Singlet',
    2: 'Dublet',
    3: 'Triplet', 
    4: 'Kwadruplet',
    5: 'Kwintet'
}

# Nazwy dla wartości Λ (abs_m)
LAMBDA_NAMES = {
    0: 'Σ',
    1: 'Π',
    2: 'Δ',
    3: 'Φ',
    4: 'Γ'
}

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def print_state_statistics(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    query = """
    SELECT 
        abs_m,
        multiplicity,
        COUNT(DISTINCT state_num) as num_states
    FROM calculations
    WHERE multiplicity IN (1, 3, 5) AND abs_m BETWEEN 0 AND 4
    GROUP BY abs_m, multiplicity
    ORDER BY abs_m, multiplicity
    """
    df = pd.read_sql(query, conn)
    conn.close()
    
    df['lambda_name'] = df['abs_m'].map(lambda x: LAMBDA_NAMES.get(int(x), '?'))
    df['mult_name'] = df['multiplicity'].map(lambda x: MULTIPLICITY_NAMES.get(int(x), '?'))
    
    print("\nStatystyki stanów wg Λ i multipletowości:")
    print(df[['lambda_name', 'mult_name', 'num_states']].to_string(index=False))

def fetch_data():
    conn = get_db_connection()
    query = """
    SELECT distance, state_num, energy, abs_m, multiplicity 
    FROM calculations 
    WHERE multiplicity IN (1, 3, 5) AND abs_m BETWEEN 0 AND 4
    ORDER BY distance, abs_m, multiplicity, energy
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def plot_energy_curves(data):
    plt.figure(figsize=(18, 12))
    ax = plt.gca()
    
    for (abs_m, mult), group in data.groupby(['abs_m', 'multiplicity']):
        abs_m_int = int(abs_m)
        mult_int = int(mult)
        
        # Kolor głównie zależy od Λ, z lekką modyfikacją dla multipletowości
        base_color = LAMBDA_COLORS.get(abs_m_int, '#777777')
        mult_color = MULTIPLICITY_COLORS.get(mult_int, '#cccccc')
        
        line_style = MULTIPLICITY_STYLES.get(mult_int, '-')
        lambda_name = LAMBDA_NAMES.get(abs_m_int, f'Λ={abs_m}')
        mult_name = MULTIPLICITY_NAMES.get(mult_int, f'M={mult}')
        
        for state in group['state_num'].unique():
            state_data = group[group['state_num'] == state]
            
            # Mieszamy kolory Λ i multipletowości
            line_color = base_color  # Można zmienić na mult_color jeśli wolisz
            
            ax.plot(
                state_data['distance'],
                state_data['energy'],
                color=line_color,
                linestyle=line_style,
                linewidth=2,
                marker='o',
                markersize=5,
                markeredgecolor='none',
                alpha=0.8,
                label=f"{lambda_name} {mult_name}" if state == group['state_num'].min() else ""
            )
            
            # Podpisz końce krzywych
            last_point = state_data.iloc[-1]
            ax.text(
                last_point['distance'] + 0.05,
                last_point['energy'],
                f"{lambda_name}-{state} ({mult_name})",
                color=line_color,
                fontsize=9,
                ha='left',
                va='center'
            )

    # Podwójna legenda
    from matplotlib.patches import Patch
    
    # Legenda dla Λ (kolor)
    lambda_legend = [Patch(color=color, label=LAMBDA_NAMES[m]) 
                    for m, color in LAMBDA_COLORS.items()]
    
    # Legenda dla multipletowości (styl linii)
    mult_legend = [Line2D([0], [0], color='black', linestyle=style, 
                  label=MULTIPLICITY_NAMES[m]) 
                 for m, style in MULTIPLICITY_STYLES.items()]
    
    # Dodanie pierwszej legendy (Λ)
    leg1 = ax.legend(handles=lambda_legend, title="Symetrie (Λ)",
                    loc='upper right',
                    fontsize=10)
    
    # Dodanie drugiej legendy (multipletowość)
    ax.add_artist(leg1)
    ax.legend(handles=mult_legend, title="Multipletowość",
             loc='lower right',
             fontsize=10)

    plt.title("Krzywe energii elektronowej z podziałem na Λ i multipletowość", 
             pad=25, fontsize=16)
    plt.xlabel("Odległość międzyjądrowa [Å]", fontsize=14)
    plt.ylabel("Energia [Hartree]", fontsize=14)
    plt.grid(True, alpha=0.2)
    plt.tight_layout()

def main():
    data = fetch_data()
    plot_energy_curves(data)
    plt.savefig("energy_curves_lambda_and_mult.png", dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    print_state_statistics()
    main()