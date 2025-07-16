import os
from collections import defaultdict

def extract_distance_from_filename(filename):
    """Wyciąga odległość z nazwy pliku (format: O2.X.YYYY.rassi.output)."""
    parts = os.path.basename(filename).split('.')
    return float(f"{parts[1]}.{parts[2]}")



def parse_jobiph_section(lines, current_line_idx, current_data):
    """Parsuje sekcję JOBIPH z wykorzystaniem 'NR OF CONFIG' jako znacznika końca."""
    line = lines[current_line_idx].strip()
    
    # Rozpoznawanie nagłówka sekcji
    if line.startswith("Specific data for JOBIPH file"):
        if current_data:  # Jeśli już trwa parsowanie innej sekcji
            return current_data, True  # Zakończ poprzednią sekcję
            
        file_name = line.split("JOBIPH file")[-1].strip()
        return {
            "file": file_name,
            "irrep": None,
            "multiplicity": None,
            "states": []
        }, False
    
    # Znacznik końca sekcji po nim szukamy koljenej sekcji
    elif "NR OF CONFIG" in line and current_data:
        return current_data, True
    
    # Parsowanie danych wewnątrz sekcji
    elif current_data:
        if "STATE IRREP:" in line:
            current_data["irrep"] = int(line.split()[-1])
        elif "SPIN MULTIPLICITY:" in line:
            current_data["multiplicity"] = int(line.split()[-1])
        elif "STATE NR:" in line:
            current_data["states"].append(int(line.split()[-1]))
        elif "States included from this file:" in line and current_line_idx + 1 < len(lines):
            next_line = lines[current_line_idx + 1].strip()
            if next_line:
                current_data["states"] = [int(s) for s in next_line.split() if s.isdigit()]
    
    return current_data, False

def parse_states_mapping(lines, current_line_idx, states_mapping):
    """Parsuje mapowanie stanów z numeracją JOBIPH."""
    line = lines[current_line_idx]
    
    if line.strip().startswith("State:") and current_line_idx + 2 < len(lines):
        states = list(map(int, line.split()[1:21]))
        jobiph_indices = list(map(int, lines[current_line_idx + 1].split()[1:21]))
        roots = list(map(int, lines[current_line_idx + 2].split()[2:22]))
        
        for state, jobiph_idx, root in zip(states, jobiph_indices, roots):
            # Mapowanie indeksów JOBIPH:
            # 1 → JOBIPH (bez numeru)
            # 2 → JOBIPH01
    
            if jobiph_idx == 1:
                jobiph_name = "JOBIPH"
            else:
                jobiph_name = f"JOBIPH{jobiph_idx-1:02d}"
            
            states_mapping[state].append({
                'jobiph': jobiph_name,
                'root': root
            })
    return states_mapping

def parse_energy_line(line, energies):
    """Parsuje linie z energiami."""
    if "RASSI State" in line and "Total energy:" in line:
        parts = line.split()
        state_num = None
        energy = None
        
        for j, part in enumerate(parts):
            if part.isdigit():
                state_num = int(part)
            elif ":" in part and part.replace(".", "").replace("-", "").isdigit():
                energy = float(part.replace(":", ""))
            elif part.startswith("-") and part.replace(".", "").replace("-", "").isdigit():
                energy = float(part)
        
        if state_num is not None and energy is not None:
            energies[state_num] = energy
    return energies

def parse_single_file(file_path):
    """Główna funkcja parsująca pojedynczy plik."""
    results = {
        'distance': extract_distance_from_filename(file_path),
        'states_mapping': defaultdict(list),
        'energies': {},
        'jobiph_data': [],
        'abs_m': {},
        'num_states': 0
    }

    abs_m_section = False
    print(f"\n=== Analizuję plik: {file_path} ===")  # Debug

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    current_data = None
    for i, line in enumerate(lines):
        # Liczba stanów
        if "Nr of states:" in line:
            results['num_states'] = int(line.split()[-1])
            print(f"Liczba stanów: {results['num_states']}")  # Debug
        
        # Sekcje JOBIPH
        current_data, should_append = parse_jobiph_section(lines, i, current_data)
        if should_append:
            print(f"Znaleziono JOBIPH: {current_data['file']}")  # Debug
            print(f"  - Irrep: {current_data['irrep']}")  # Debug
            print(f"  - Multiplicity: {current_data['multiplicity']}")  # Debug
            print(f"  - States: {current_data['states']}")  # Debug
            results['jobiph_data'].append(current_data)
            current_data = None
        
        # Mapowanie stanów
        results['states_mapping'] = parse_states_mapping(lines, i, results['states_mapping'])
        
        # Energia
        results['energies'] = parse_energy_line(line, results['energies'])
        
        # SF State i Abs_M
        if 'SF State' in line and 'Abs_M' in line:
            abs_m_section = True
            continue
        
        if abs_m_section:
            parts = line.strip().split()
            if len(parts) >= 6:
                try:
                    state = int(parts[0])
                    abs_m = float(parts[5])
                    results['abs_m'][state] = abs_m
                except (ValueError, IndexError):
                    pass
            else:
                abs_m_section = False

    if current_data:
        print(f"Znaleziono JOBIPH (na końcu pliku): {current_data['file']}")  # Debug
        results['jobiph_data'].append(current_data)

    # Dodatkowe debugowanie mapowania stanów
    print("\nMapowanie stanów:")
    for state, mappings in results['states_mapping'].items():
        print(f"State {state}:")
        for mapping in mappings:
            print(f"  - JOBIPH: {mapping['jobiph']}, Root: {mapping['root']}")

    # Debugowanie energii
    print("\nEnergie:")
    for state, energy in results['energies'].items():
        print(f"State {state}: {energy}")

    # Debugowanie Abs_M
    print("\nAbs_M:")
    for state, abs_m in results['abs_m'].items():
        print(f"State {state}: {abs_m}")

    return results