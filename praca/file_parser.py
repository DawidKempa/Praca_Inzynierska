import os
from collections import defaultdict

def extract_distance_from_filename(filename):
    distance_parts = os.path.basename(filename).split('.')
    return float(f"{distance_parts[1]}.{distance_parts[2]}")

def parse_jobiph_section(lines, current_line_idx, current_data): 
    line = lines[current_line_idx]
    if "Specific data for JOBIPH file" in line:
        if current_data:
            return current_data, True
        current_section = line.split()[-1]
        return {
            "file": current_section,
            "irrep": None,
            "multiplicity": None
        }, False
    
    elif "STATE IRREP:" in line and current_data:
        current_data["irrep"] = int(line.split()[-1])
    elif "SPIN MULTIPLICITY:" in line and current_data:
        current_data["multiplicity"] = int(line.split()[-1])
    
    return current_data, False

def parse_states_mapping(lines, current_line_idx, states_mapping): 

    line = lines[current_line_idx]
    if line.strip().startswith("State:") and current_line_idx + 2 < len(lines):
        states = list(map(int, line.split()[1:21]))
        jobiphs = list(map(int, lines[current_line_idx + 1].split()[1:21]))
        roots = list(map(int, lines[current_line_idx + 2].split()[2:22]))
        
        for state, jobiph, root in zip(states, jobiphs, roots):
            states_mapping[state].append({
                'jobiph': f"JOBIPH{jobiph-1:02d}" if jobiph > 1 else "JOBIPH",
                'root': root
            })
    return states_mapping

def parse_energy_line(line, energies): 
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

    results = {
        'states_mapping': defaultdict(list),
        'energies': {},
        'distance': None,
        'num_states': 0,
        'jobiph_data': []
    }

    results['distance'] = extract_distance_from_filename(file_path)

    with open(file_path, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()
    
    current_data = None
    for i, line in enumerate(all_lines):

        if "Nr of states:" in line:
            results['num_states'] = int(line.split()[-1])

        current_data, should_append = parse_jobiph_section(all_lines, i, current_data)
        if should_append:
            results['jobiph_data'].append(current_data)
            current_data = None
        
        results['states_mapping'] = parse_states_mapping(all_lines, i, results['states_mapping'])
        
        results['energies'] = parse_energy_line(line, results['energies'])

    if current_data:
        results['jobiph_data'].append(current_data)

    return results