import os

def print_file_header(file_path, distance, num_states): 
    print(f"\n{' ANALIZA PLIKU ':=^60}")
    print(f"{'Ścieżka:':<12} {os.path.abspath(file_path)}")
    print(f"{'Odległość R:':<12} {distance*2} Å")
    print(f"{'Liczba stanów:':<12} {num_states}\n")

def print_jobiph_data(jobiph_data):
    print(f"{' DANE JOBIPH ':-^60}")
    for data in jobiph_data:
        print(f"{data['file']}:   IRREP = {data['irrep']}   MULTIPLICITY = {data['multiplicity']}")
        print("-" * 30)

def print_states_mapping(states_mapping, energies, abs_m):
    if states_mapping:
        print(f"\n{' MAPOWANIE STANÓW Z ENERGIAMI I Abs_M ':-^60}")
        print(f"{'State':<6} | {'JobIph':<8} | {'Root':<4} | {'Energy (Hartree)':<15} | {'Abs_M':<6}")
        print("-" * 60)
        
        for state in sorted(states_mapping.keys()):
            energy = energies.get(state, float('nan'))
            abs_m_value = abs_m.get(state, float('nan'))
            mappings = states_mapping.get(state, [{'jobiph': 'N/A', 'root': 'N/A'}])
            
            for mapping in mappings:
                print(f"{state:<6} | {mapping['jobiph']:<8} | {mapping['root']:<4} | {energy:>15.6f} | {abs_m_value:>6.1f}")
    else:
        print("\nNie znaleziono danych o mapowaniu stanów!")

def print_energy_summary(energies):

    if energies:
        min_energy = min(energies.values())
        print(f"\nEnergia stanu podstawowego: {min_energy:.12f} Hartree")
    else:
        print("\nBrak danych energetycznych")

def print_error(e):
    """Drukuje informacje o błędzie"""
    print(f"\n{' BŁĄD ':=^60}")
    print(f"Typ: {type(e).__name__}")
    print(f"Komunikat: {str(e)}")
    import traceback
    traceback.print_exc()